import React from 'react';
import { Mic, Volume2, Sparkles, Radio } from 'lucide-react';
import { t } from '../services/i18n';

export default function VoiceWave({
  isListening,
  isSpeaking,
  isLoading,
  onMicClick,
  hasSpeechRecognition,
  currentLang
}) {
  return (
    <div className="flex flex-col items-center justify-center py-6">
      
      {/* Orb Outer Animation Rings */}
      <div className="relative flex items-center justify-center">
        
        {/* Pulsing Ripple Rings when listening */}
        {isListening && (
          <>
            <div className="absolute w-44 h-44 rounded-full border border-cyan-400/40 animate-ping" />
            <div className="absolute w-56 h-56 rounded-full border border-cyan-500/20 animate-pulse" />
          </>
        )}

        {/* Audio Wave Ring when AI is speaking */}
        {isSpeaking && (
          <div className="absolute w-48 h-48 rounded-full border-2 border-emerald-400/50 animate-spin" style={{ animationDuration: '6s' }} />
        )}

        {/* Center Interactive Orb Button */}
        <button
          onClick={onMicClick}
          title={isListening ? "Listening... Click to stop" : "Click to speak with RetailMate AI"}
          className={`relative z-10 w-32 h-32 rounded-full flex flex-col items-center justify-center transition-all duration-500 shadow-2xl ${
            isListening
              ? 'bg-gradient-to-tr from-cyan-500 via-blue-500 to-indigo-600 shadow-cyan-500/50 scale-105 orb-listening'
              : isSpeaking
              ? 'bg-gradient-to-tr from-emerald-500 to-cyan-600 shadow-emerald-500/40 scale-105'
              : isLoading
              ? 'bg-gradient-to-tr from-indigo-600 to-purple-600 animate-pulse'
              : 'bg-gradient-to-tr from-slate-900 via-slate-800 to-slate-900 border-2 border-slate-700 hover:border-cyan-500/50 hover:shadow-cyan-500/20 group'
          }`}
        >
          {/* Inner Glow Core */}
          <div className={`w-24 h-24 rounded-full flex items-center justify-center transition-all ${
            isListening ? 'bg-cyan-400/20 text-white' : 'bg-slate-950/60 text-cyan-400 group-hover:text-cyan-300'
          }`}>
            {isLoading ? (
              <Radio className="w-10 h-10 animate-spin text-cyan-400" />
            ) : isListening ? (
              <Mic className="w-10 h-10 animate-bounce text-white" />
            ) : isSpeaking ? (
              <Volume2 className="w-10 h-10 animate-pulse text-emerald-400" />
            ) : (
              <Mic className="w-10 h-10 transition-transform group-hover:scale-110" />
            )}
          </div>
        </button>
      </div>

      {/* Voice Status Text */}
      <div className="mt-5 text-center">
        <div className="flex items-center justify-center gap-2">
          {isListening ? (
            <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/20 border border-cyan-500/30 text-cyan-300 text-xs font-semibold animate-pulse">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" /> {t('listeningState', currentLang)}
            </span>
          ) : isSpeaking ? (
            <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/20 border border-emerald-500/30 text-emerald-300 text-xs font-semibold">
              <Volume2 className="w-3.5 h-3.5 animate-pulse" /> {t('speakingState', currentLang)}
            </span>
          ) : isLoading ? (
            <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/20 border border-purple-500/30 text-purple-300 text-xs font-semibold">
              <Sparkles className="w-3.5 h-3.5 animate-spin" /> {t('queryingRagState', currentLang)}
            </span>
          ) : (
            <span className="text-xs text-slate-400 font-medium flex items-center gap-1.5">
              <Radio className="w-3.5 h-3.5 text-cyan-400" /> {t('tapMicInstruction', currentLang)}
            </span>
          )}
        </div>

        {!hasSpeechRecognition && (
          <p className="mt-1 text-[11px] text-amber-400/80">
            (Speech Recognition not supported in this browser window; text input fully available)
          </p>
        )}
      </div>

    </div>
  );
}
