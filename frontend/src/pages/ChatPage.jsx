import React, {
  useState,
  useRef,
  useEffect,
} from 'react';

import {
  Send,
  Bot,
  User,
  Sparkles,
  Mic,
  RefreshCw,
  AlertTriangle,
  Trash2,
  CheckCircle2,
} from 'lucide-react';

import ProductCard from '../components/ProductCard';

import {
  queryAssistant,
} from '../services/api';

import {
  useSpeech,
} from '../hooks/useSpeech';

import {
  t,
} from '../services/i18n';


export default function ChatPage({
  messages,
  onAddChatMessage,
  onClearChat,
  onLocateAisle,
  voiceEnabled,
  currentLang,
}) {
  const [inputText, setInputText] = useState('');

  const [isLoading, setIsLoading] =
    useState(false);

  const [errorState, setErrorState] =
    useState(null);

  const messagesEndRef =
    useRef(null);


  /*
   * ---------------------------------------------------------
   * SPEECH
   * ---------------------------------------------------------
   */

  const {
    isListening,
    transcript,
    startListening,
    stopListening,
    speakText,
    hasSpeechRecognition,
  } = useSpeech(currentLang);


  /*
   * ---------------------------------------------------------
   * PUT STT TRANSCRIPT INTO INPUT BOX
   * ---------------------------------------------------------
   */

  useEffect(() => {
    if (transcript) {
      setInputText(transcript);
    }
  }, [transcript]);


  /*
   * ---------------------------------------------------------
   * SCROLL CHAT TO BOTTOM
   * ---------------------------------------------------------
   */

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({
      behavior: 'smooth',
    });
  };


  useEffect(() => {
    scrollToBottom();
  }, [
    messages,
    isLoading,
  ]);


  /*
   * ---------------------------------------------------------
   * SEND MESSAGE
   * ---------------------------------------------------------
   */

  const handleSendMessage = async (
    textToSend
  ) => {
    const q = (
      textToSend || inputText
    ).trim();


    /*
     * Don't send empty messages
     */
    if (!q || isLoading) {
      return;
    }


    /*
     * Stop microphone if currently listening
     */
    if (isListening) {
      stopListening();
    }


    /*
     * Clear input
     */
    setInputText('');


    /*
     * Clear previous error
     */
    setErrorState(null);


    /*
     * Show loading
     */
    setIsLoading(true);


    /*
     * Add user's message to chat
     */
    onAddChatMessage({
      sender: 'user',

      text: q,

      time: new Date().toLocaleTimeString(),
    });


    try {
      /*
       * -----------------------------------------------------
       * IMPORTANT CHANGE
       * -----------------------------------------------------
       *
       * We now pass currentLang to the Agent Service.
       *
       * Example:
       *
       * English -> en
       * Hindi   -> hi
       * Kannada -> kn
       */
      const res = await queryAssistant(
        q,
        'demo-user',
        currentLang
      );


      /*
       * Stop loading
       */
      setIsLoading(false);


      /*
       * Make sure response exists
       */
      if (!res || !res.data) {
        throw new Error(
          'Agent Service returned an empty response.'
        );
      }


      /*
       * Get answer
       */
      const answerText =
        res.data.answer ||
        'Query processed.';


      /*
       * -----------------------------------------------------
       * ADD AI MESSAGE
       * -----------------------------------------------------
       */

      onAddChatMessage({
        sender: 'ai',

        text: answerText,

        products:
          res.data.products || [],

        sources:
          res.data.sources || [],

        /*
         * This should now be false when using the real
         * Agent/RAG service.
         */
        isMock:
          res.isMock === true,

        time:
          new Date().toLocaleTimeString(),
      });


      /*
       * -----------------------------------------------------
       * TEXT TO SPEECH
       * -----------------------------------------------------
       *
       * useSpeech() now sends this answer to:
       *
       * POST http://127.0.0.1:8003/api/voice/tts
       *
       * instead of directly using browser speech synthesis.
       */
      if (voiceEnabled) {
        speakText(
          answerText,
          currentLang
        );
      }
    } catch (err) {
      /*
       * -----------------------------------------------------
       * REAL ERROR
       * -----------------------------------------------------
       *
       * There is intentionally NO mock fallback here.
       *
       * If Agent :8003 is down, we want to see the error
       * instead of receiving fake Pegasus data.
       */

      console.error(
        '[RetailMate Chat] Error:',
        err
      );


      setIsLoading(false);


      setErrorState({
        failedQuery: q,

        message:
          err?.message ||
          'Failed to communicate with the RetailMate Agent Service. Please verify that Agent Service is running on port 8003.',
      });
    }
  };


  /*
   * ---------------------------------------------------------
   * UI
   * ---------------------------------------------------------
   */

  return (
    <div
      className="
        max-w-4xl
        mx-auto
        h-[calc(100vh-140px)]
        flex
        flex-col
        bg-slate-900/80
        border
        border-slate-800
        rounded-3xl
        overflow-hidden
        shadow-2xl
        backdrop-blur-md
        animate-fadeIn
      "
    >

      {/* =====================================================
          CHAT TOP BAR
          ===================================================== */}

      <div
        className="
          p-4
          px-6
          bg-slate-950/80
          border-b
          border-slate-800
          flex
          items-center
          justify-between
        "
      >

        <div
          className="
            flex
            items-center
            gap-3
          "
        >

          <div
            className="
              w-10
              h-10
              rounded-2xl
              bg-cyan-500/10
              border
              border-cyan-500/20
              text-cyan-400
              flex
              items-center
              justify-center
            "
          >
            <Bot className="w-5 h-5" />
          </div>


          <div>

            <h3
              className="
                font-bold
                text-slate-100
                text-sm
                flex
                items-center
                gap-2
              "
            >

              {t(
                'chatTitle',
                currentLang
              )}

              <span
                className="
                  w-2
                  h-2
                  rounded-full
                  bg-emerald-400
                  animate-pulse
                "
              />

            </h3>


            <p
              className="
                text-[11px]
                text-slate-400
              "
            >
              {t(
                'chatSubtitle',
                currentLang
              )}
            </p>

          </div>

        </div>


        <button
          onClick={onClearChat}
          title={t(
            'clearHistory',
            currentLang
          )}
          className="
            p-2
            text-slate-400
            hover:text-rose-400
            hover:bg-slate-900
            rounded-xl
            transition-colors
            text-xs
            font-semibold
            flex
            items-center
            gap-1.5
            border
            border-slate-800
          "
        >

          <Trash2 className="w-4 h-4" />

          {t(
            'clearHistory',
            currentLang
          )}

        </button>

      </div>


      {/* =====================================================
          MESSAGE TIMELINE
          ===================================================== */}

      <div
        className="
          flex-1
          overflow-y-auto
          p-6
          space-y-6
        "
      >

        {messages.length === 0 ? (

          <div
            className="
              h-full
              flex
              flex-col
              items-center
              justify-center
              text-center
              space-y-4
              text-slate-500
            "
          >

            <Sparkles
              className="
                w-10
                h-10
                text-cyan-500/40
                animate-pulse
              "
            />

            <h4
              className="
                font-bold
                text-slate-400
              "
            >
              {t(
                'noHistoryTitle',
                currentLang
              )}
            </h4>

            <p
              className="
                text-xs
                max-w-xs
                leading-relaxed
              "
            >
              {t(
                'noHistoryDesc',
                currentLang
              )}
            </p>

          </div>

        ) : (

          messages.map(
            (msg, index) => {

              const isUser =
                msg.sender === 'user';


              return (
                <div
                  key={index}
                  className={`
                    flex
                    gap-3
                    ${
                      isUser
                        ? 'justify-end'
                        : 'justify-start'
                    }
                    animate-fadeIn
                  `}
                >

                  {/* AI AVATAR */}

                  {!isUser && (

                    <div
                      className="
                        w-8
                        h-8
                        rounded-xl
                        bg-gradient-to-tr
                        from-cyan-500
                        to-blue-600
                        text-white
                        flex
                        items-center
                        justify-center
                        shrink-0
                        mt-1
                        shadow-md
                      "
                    >

                      <Bot
                        className="w-4 h-4"
                      />

                    </div>

                  )}


                  {/* MESSAGE */}

                  <div
                    className="
                      max-w-[82%]
                      space-y-3
                    "
                  >

                    <div
                      className={`
                        p-4
                        rounded-3xl
                        text-sm
                        leading-relaxed
                        ${
                          isUser
                            ? `
                              bg-gradient-to-r
                              from-cyan-500
                              to-blue-600
                              text-white
                              font-medium
                              rounded-tr-none
                              shadow-lg
                              shadow-cyan-500/20
                            `
                            : `
                              bg-slate-950
                              border
                              border-slate-800
                              text-slate-200
                              rounded-tl-none
                              shadow-inner
                            `
                        }
                      `}
                    >

                      {msg.text}


                      {/* SOURCES */}

                      {!isUser &&
                        msg.sources &&
                        msg.sources.length > 0 && (

                          <div
                            className="
                              mt-2
                              pt-2
                              border-t
                              border-slate-800
                              text-[10px]
                              text-slate-500
                              font-mono
                              flex
                              items-center
                              gap-1
                            "
                          >

                            <CheckCircle2
                              className="
                                w-3
                                h-3
                                text-cyan-400
                              "
                            />

                            {msg.sources.join(
                              ', '
                            )}

                          </div>

                        )}

                    </div>


                    {/* PRODUCT CARDS */}

                    {!isUser &&
                      msg.products &&
                      msg.products.length > 0 && (

                        <div
                          className="
                            grid
                            grid-cols-1
                            sm:grid-cols-2
                            gap-3
                            pt-1
                          "
                        >

                          {msg.products.map(
                            (p) => (

                              <ProductCard
                                key={
                                  p.id ||
                                  p.product_id
                                }

                                product={p}

                                currentLang={
                                  currentLang
                                }

                                onLocateAisle={
                                  onLocateAisle
                                }
                              />

                            )
                          )}

                        </div>

                      )}


                    {/* TIMESTAMP / MOCK INDICATOR */}

                    <span
                      className={`
                        block
                        text-[10px]
                        text-slate-500
                        px-1
                        font-mono
                        ${
                          isUser
                            ? 'text-right'
                            : 'text-left'
                        }
                      `}
                    >

                      {msg.time}

                      {msg.isMock &&
                        ' • Mock RAG'}

                    </span>

                  </div>


                  {/* USER AVATAR */}

                  {isUser && (

                    <div
                      className="
                        w-8
                        h-8
                        rounded-xl
                        bg-slate-800
                        border
                        border-slate-700
                        text-slate-200
                        flex
                        items-center
                        justify-center
                        shrink-0
                        mt-1
                      "
                    >

                      <User
                        className="w-4 h-4"
                      />

                    </div>

                  )}

                </div>
              );
            }
          )

        )}


        {/* =================================================
            LOADING
            ================================================= */}

        {isLoading && (

          <div
            className="
              flex
              gap-3
              justify-start
              items-center
              animate-pulse
            "
          >

            <div
              className="
                w-8
                h-8
                rounded-xl
                bg-cyan-500/20
                text-cyan-400
                flex
                items-center
                justify-center
              "
            >

              <Bot
                className="w-4 h-4"
              />

            </div>


            <div
              className="
                p-4
                rounded-3xl
                bg-slate-950
                border
                border-slate-800
                text-slate-400
                text-xs
                flex
                items-center
                gap-2
              "
            >

              <RefreshCw
                className="
                  w-4
                  h-4
                  animate-spin
                  text-cyan-400
                "
              />

              <span>
                {t(
                  'queryingRagState',
                  currentLang
                )}
              </span>

            </div>

          </div>

        )}


        {/* =================================================
            ERROR
            ================================================= */}

        {errorState && (

          <div
            className="
              p-4
              rounded-2xl
              bg-rose-500/10
              border
              border-rose-500/30
              text-rose-300
              text-xs
              flex
              items-center
              justify-between
              gap-3
            "
          >

            <div
              className="
                flex
                items-center
                gap-2
              "
            >

              <AlertTriangle
                className="
                  w-4
                  h-4
                  text-rose-400
                  shrink-0
                "
              />

              <span>
                {errorState.message}
              </span>

            </div>


            <button
              onClick={() =>
                handleSendMessage(
                  errorState.failedQuery
                )
              }
              className="
                px-3
                py-1.5
                rounded-xl
                bg-rose-500/20
                hover:bg-rose-500/30
                text-rose-200
                font-semibold
                text-xs
                transition-colors
                shrink-0
              "
            >

              {t(
                'retryBtn',
                currentLang
              )}

            </button>

          </div>

        )}


        <div
          ref={messagesEndRef}
        />

      </div>


      {/* =====================================================
          CHAT INPUT
          ===================================================== */}

      <div
        className="
          p-4
          bg-slate-950
          border-t
          border-slate-800
        "
      >

        <form
          onSubmit={(e) => {
            e.preventDefault();

            handleSendMessage();
          }}

          className="
            flex
            items-center
            gap-2
          "
        >

          {/* MICROPHONE */}

          {hasSpeechRecognition && (

            <button
              type="button"

              onClick={
                isListening
                  ? stopListening
                  : startListening
              }

              className={`
                p-3
                rounded-2xl
                border
                transition-all
                ${
                  isListening
                    ? `
                      bg-cyan-500
                      text-slate-950
                      border-cyan-400
                      animate-pulse
                    `
                    : `
                      bg-slate-900
                      border-slate-800
                      text-slate-400
                      hover:text-white
                      hover:bg-slate-800
                    `
                }
              `}
            >

              <Mic
                className="w-5 h-5"
              />

            </button>

          )}


          {/* TEXT INPUT */}

          <input
            type="text"

            value={inputText}

            onChange={(e) =>
              setInputText(
                e.target.value
              )
            }

            placeholder={t(
              'typePlaceholder',
              currentLang
            )}

            disabled={isLoading}

            className="
              flex-1
              bg-slate-900
              border
              border-slate-800
              focus:border-cyan-500
              rounded-2xl
              px-5
              py-3.5
              text-sm
              text-slate-100
              placeholder-slate-500
              focus:outline-none
              focus:ring-2
              focus:ring-cyan-500/20
            "
          />


          {/* SEND */}

          <button
            type="submit"

            disabled={
              !inputText.trim() ||
              isLoading
            }

            className="
              p-3.5
              rounded-2xl
              bg-gradient-to-r
              from-cyan-500
              to-blue-600
              hover:from-cyan-400
              hover:to-blue-500
              disabled:opacity-40
              text-white
              font-semibold
              transition-all
              shadow-md
            "
          >

            <Send
              className="w-4 h-4"
            />

          </button>

        </form>

      </div>

    </div>
  );
}