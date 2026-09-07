import { useState, useEffect, useCallback, useRef } from 'react';
import { getSpeechLanguage } from '../services/i18n';

const AGENT_SERVICE_URL =
  import.meta.env.VITE_AGENT_SERVICE_URL || 'http://127.0.0.1:8003';

export function useSpeech(currentLangCode = 'en') {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [hasSpeechRecognition, setHasSpeechRecognition] = useState(false);

  const recognitionRef = useRef(null);
  const audioRef = useRef(null);
  const speechTimingRef = useRef({});

  const getSpeechLangCode = useCallback((code) => {
    return getSpeechLanguage(code);
  }, []);

  // =========================
  // SPEECH TO TEXT
  // =========================
  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition ||
      window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setHasSpeechRecognition(false);
      return;
    }

    setHasSpeechRecognition(true);

    const recognition = new SpeechRecognition();

    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = getSpeechLangCode(currentLangCode);

    recognition.onstart = () => {
      speechTimingRef.current = {
        microphone_start: new Date().toISOString(),
        microphone_start_ms: performance.now(),
        stt_request_start: new Date().toISOString(),
        stt_request_start_ms: performance.now(),
        stt_first_interim: null,
        stt_final_transcript: null,
      };
      setIsListening(true);
    };

    recognition.onresult = (event) => {
      let resultText = '';

      for (
        let i = event.resultIndex;
        i < event.results.length;
        i++
      ) {
        const result = event.results[i][0];
        resultText += result.transcript;

        if (
          !result.isFinal &&
          !speechTimingRef.current.stt_first_interim
        ) {
          speechTimingRef.current.stt_first_interim =
            new Date().toISOString();
          speechTimingRef.current.stt_first_interim_ms =
            performance.now();
        }

        if (result.isFinal) {
          speechTimingRef.current.stt_final_transcript =
            new Date().toISOString();
          speechTimingRef.current.stt_final_transcript_ms =
            performance.now();
          speechTimingRef.current.transcript = resultText;
        }
      }

      setTranscript(resultText);
    };

    recognition.onerror = (event) => {
      console.warn(
        '[RetailMate STT] Error:',
        event.error
      );

      setIsListening(false);
    };

    recognition.onend = () => {
      speechTimingRef.current.microphone_stop =
        new Date().toISOString();
      speechTimingRef.current.microphone_stop_ms =
        performance.now();
      speechTimingRef.current.stt_latency_ms =
        speechTimingRef.current.stt_final_transcript_ms &&
        speechTimingRef.current.stt_request_start_ms
          ? speechTimingRef.current.stt_final_transcript_ms -
            speechTimingRef.current.stt_request_start_ms
          : null;

      console.info(
        '[Voice Pipeline] STT',
        speechTimingRef.current
      );
      setIsListening(false);
    };

    recognitionRef.current = recognition;

    return () => {
      try {
        recognition.stop();
      } catch {
        // Already stopped.
      }

      recognitionRef.current = null;
    };
  }, [currentLangCode, getSpeechLangCode]);

  // =========================
  // START LISTENING
  // =========================
  const startListening = useCallback(() => {
    if (!recognitionRef.current || isListening) {
      return;
    }

    try {
      setTranscript('');

      recognitionRef.current.lang =
        getSpeechLangCode(currentLangCode);

      recognitionRef.current.start();
    } catch (error) {
      console.error(
        '[RetailMate STT] Start failed:',
        error
      );
    }
  }, [
    isListening,
    currentLangCode,
    getSpeechLangCode,
  ]);

  // =========================
  // STOP LISTENING
  // =========================
  const stopListening = useCallback(() => {
    if (!recognitionRef.current) {
      return;
    }

    try {
      recognitionRef.current.stop();
    } catch {
      // Already stopped.
    }

    setIsListening(false);
  }, []);

  // =========================
  // TEXT TO SPEECH
  // Member 4 :8003
  // =========================
  const speakText = useCallback(
    async (text, langCode = currentLangCode) => {
      if (!voiceEnabled || !text?.trim()) {
        return;
      }

      // Stop previous generated audio
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
        audioRef.current = null;
      }

      // Stop browser TTS
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }

      setIsSpeaking(true);

      const ttsStartedAt = new Date().toISOString();
      const ttsStartedMs = performance.now();

      try {
        const streamingEnabled =
          import.meta.env.VITE_ENABLE_STREAMING_TTS !== 'false';

        if (
          streamingEnabled &&
          'MediaSource' in window &&
          MediaSource.isTypeSupported('audio/mpeg')
        ) {
          const streamResponse = await fetch(
            `${AGENT_SERVICE_URL}/api/voice/tts/stream`,
            {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                text: text.trim(),
                language: langCode,
                speed: 0.95,
              }),
            }
          );

          if (streamResponse.ok && streamResponse.body) {
            const mediaSource = new MediaSource();
            const audio = new Audio();
            const streamUrl = URL.createObjectURL(mediaSource);
            const reader = streamResponse.body.getReader();
            let firstChunkAt = null;
            let firstChunkMs = null;

            audio.src = streamUrl;
            audioRef.current = audio;
            audio.onended = () => {
              setIsSpeaking(false);
              audioRef.current = null;
              URL.revokeObjectURL(streamUrl);
            };

            const appendChunk = (sourceBuffer, chunk) =>
              new Promise((resolve, reject) => {
                const finish = () => {
                  sourceBuffer.removeEventListener(
                    'updateend',
                    finish
                  );
                  sourceBuffer.removeEventListener(
                    'error',
                    fail
                  );
                  resolve();
                };
                const fail = () => reject(
                  new Error('Audio stream buffer failed.')
                );

                sourceBuffer.addEventListener(
                  'updateend',
                  finish,
                  { once: true }
                );
                sourceBuffer.addEventListener(
                  'error',
                  fail,
                  { once: true }
                );
                sourceBuffer.appendBuffer(chunk);
              });

            const streamFinished = new Promise((resolve, reject) => {
              mediaSource.addEventListener(
                'sourceopen',
                async () => {
                  try {
                    const sourceBuffer = mediaSource.addSourceBuffer(
                      'audio/mpeg'
                    );

                    while (true) {
                      const chunk = await reader.read();

                      if (chunk.done) {
                        mediaSource.endOfStream();
                        resolve();
                        break;
                      }

                      if (!firstChunkAt) {
                        firstChunkAt = new Date().toISOString();
                        firstChunkMs = performance.now();
                      }

                      await appendChunk(
                        sourceBuffer,
                        chunk.value
                      );
                    }
                  } catch (error) {
                    reject(error);
                  }
                },
                { once: true }
              );
            });

            const playbackStarted = new Promise((resolve, reject) => {
              audio.onplaying = () => resolve({
                at: new Date().toISOString(),
                ms: performance.now(),
              });
              audio.onerror = () => reject(
                new Error('Streaming audio playback failed.')
              );
            });

            await audio.play();
            const playback = await playbackStarted;
            console.info('[Voice Pipeline] COMPLETE', {
              ...(speechTimingRef.current || {}),
              tts_request_start: ttsStartedAt,
              tts_first_audio: firstChunkAt,
              audio_playback_start: playback.at,
              tts_time_to_first_audio_ms:
                firstChunkMs - ttsStartedMs,
              total_user_perceived_latency_ms:
                speechTimingRef.current.microphone_start_ms
                  ? playback.ms -
                    speechTimingRef.current.microphone_start_ms
                  : null,
              streaming: true,
              buffering: 'MediaSource audio/mpeg chunks',
            });

            await streamFinished;
            URL.revokeObjectURL(streamUrl);
            return;
          }
        }

        const response = await fetch(
          `${AGENT_SERVICE_URL}/api/voice/tts`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              text: text.trim(),
              language: langCode,
              speed: 0.95,
            }),
          }
        );

        const responseHeadersAt = new Date().toISOString();
        const responseHeadersMs = performance.now();

        if (!response.ok) {
          throw new Error(
            `TTS service returned HTTP ${response.status}`
          );
        }

        const data = await response.json();
        const responseCompleteAt = new Date().toISOString();
        const responseCompleteMs = performance.now();

        if (!data.success || !data.audio_url) {
          throw new Error(
            'TTS service returned no audio URL'
          );
        }

        const audioUrl =
          `${AGENT_SERVICE_URL}${data.audio_url}`;

        const audio = new Audio(audioUrl);

        audioRef.current = audio;

        audio.onended = () => {
          setIsSpeaking(false);
          audioRef.current = null;
        };

        audio.onerror = (event) => {
          console.error(
            '[RetailMate TTS] Playback error:',
            event
          );

          setIsSpeaking(false);
          audioRef.current = null;
        };

        await audio.play();

        const playbackStartedAt = new Date().toISOString();
        const playbackStartedMs = performance.now();
        const timing = {
          ...(speechTimingRef.current || {}),
          tts_request_start: ttsStartedAt,
          tts_first_audio: responseHeadersAt,
          tts_complete_audio: responseCompleteAt,
          audio_playback_start: playbackStartedAt,
          tts_time_to_first_audio_ms:
            responseHeadersMs - ttsStartedMs,
          tts_total_ms:
            responseCompleteMs - ttsStartedMs,
          playback_start_latency_ms:
            playbackStartedMs - responseCompleteMs,
          total_user_perceived_latency_ms:
            speechTimingRef.current.microphone_start_ms
              ? playbackStartedMs -
                speechTimingRef.current.microphone_start_ms
              : null,
          streaming: false,
          buffering: 'complete audio response before playback',
        };

        console.info(
          '[Voice Pipeline] COMPLETE',
          timing
        );
      } catch (error) {
        console.error(
          '[RetailMate TTS] Member 4 failed:',
          error
        );

        setIsSpeaking(false);

        // Browser TTS fallback
        if ('speechSynthesis' in window) {
          const cleanText = text.replace(
            /[*_#`[\]()]/g,
            ''
          );

          const utterance =
            new SpeechSynthesisUtterance(cleanText);

          utterance.lang =
            getSpeechLangCode(langCode);

          utterance.rate = 0.95;
          utterance.pitch = 1.0;

          utterance.onstart = () => {
            setIsSpeaking(true);
          };

          utterance.onend = () => {
            setIsSpeaking(false);
          };

          utterance.onerror = () => {
            setIsSpeaking(false);
          };

          window.speechSynthesis.cancel();
          window.speechSynthesis.speak(utterance);
        }
      }
    },
    [
      voiceEnabled,
      currentLangCode,
      getSpeechLangCode,
    ]
  );

  // =========================
  // STOP SPEAKING
  // =========================
  const stopSpeaking = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current = null;
    }

    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }

    setIsSpeaking(false);
  }, []);

  return {
    // STT
    isListening,
    transcript,
    setTranscript,
    startListening,
    stopListening,
    hasSpeechRecognition,
    getSpeechTiming: () => ({
      ...speechTimingRef.current,
    }),

    // TTS
    isSpeaking,
    speakText,
    stopSpeaking,

    // Voice settings
    voiceEnabled,
    setVoiceEnabled,
  };
}