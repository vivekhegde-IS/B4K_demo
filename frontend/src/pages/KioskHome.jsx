import React, { useState, useEffect } from 'react';
import { 
  Send, 
  Sparkles, 
  Bot, 
  AlertTriangle, 
  RefreshCw, 
  Package, 
  RotateCcw,
  CheckCircle2
} from 'lucide-react';
import VoiceWave from '../components/VoiceWave';
import SuggestedPrompts from '../components/SuggestedPrompts';
import ProductCard from '../components/ProductCard';
import { queryAssistant } from '../services/api';
import { useSpeech } from '../hooks/useSpeech';
import { t } from '../services/i18n';

export default function KioskHome({ 
  onNavigateToReturns, 
  onNavigateToInventory,
  onLocateAisle,
  voiceEnabled,
  onAddChatMessage,
  currentLang
}) {
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [latestResponse, setLatestResponse] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  const {
    isListening,
    transcript,
    startListening,
    stopListening,
    isSpeaking,
    speakText,
    hasSpeechRecognition
  } = useSpeech(currentLang);

  // Sync speech transcript into input field
  useEffect(() => {
    if (transcript) {
      setInputText(transcript);
    }
  }, [transcript]);

  const handleMicToggle = () => {
    if (isListening) {
      stopListening();
    } else {
      setErrorMessage(null);
      startListening();
    }
  };

  const handleSendQuery = async (queryToSubmit) => {
    const q = (queryToSubmit || inputText).trim();
    if (!q || isLoading) return;

    if (isListening) stopListening();

    setIsLoading(true);
    setErrorMessage(null);
    setInputText('');

    // Save to global chat timeline
    onAddChatMessage({ sender: 'user', text: q, time: new Date().toLocaleTimeString() });

    try {
      const res = await queryAssistant(q, "demo-user");
      setIsLoading(false);

      if (res && res.data) {
        setLatestResponse(res);
        const answerText = res.data.answer || "I found relevant store details for your query.";
        
        // Save AI reply to global chat timeline
        onAddChatMessage({ 
          sender: 'ai', 
          text: answerText, 
          products: res.data.products || [],
          isMock: res.isMock,
          time: new Date().toLocaleTimeString()
        });

        // Speak back response in selected language
        if (voiceEnabled) {
          speakText(answerText, currentLang);
        }
      }
    } catch (err) {
      console.error("Query error:", err);
      setIsLoading(false);
      setErrorMessage("Could not connect to FastAPI server or RAG service. Please try again.");
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-fadeIn pb-12">
      
      {/* Top Banner Hero */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 border border-slate-800 p-6 lg:p-10 shadow-2xl">
        <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-8">
          <div className="space-y-3 text-center md:text-left max-w-xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-semibold">
              <Bot className="w-3.5 h-3.5" /> {t('kioskTitle', currentLang)}
            </div>
            <h2 className="text-3xl lg:text-4xl font-extrabold tracking-tight text-white">
              {t('welcomeTitle', currentLang)} <span className="bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-blue-500">{t('brandName', currentLang)}</span>
            </h2>
            <p className="text-sm text-slate-300 leading-relaxed">
              {t('welcomeSubtitle', currentLang)}
            </p>
          </div>

          {/* Quick Action Navigation Buttons */}
          <div className="flex flex-wrap md:flex-col gap-3 shrink-0">
            <button
              onClick={onNavigateToInventory}
              className="flex items-center gap-2 px-5 py-3 rounded-2xl bg-slate-950 border border-slate-800 hover:border-cyan-500/50 text-slate-200 hover:text-white font-semibold text-xs transition-all hover:scale-105 shadow-md"
            >
              <Package className="w-4 h-4 text-cyan-400" />
              <span>{t('browseInventoryBtn', currentLang)}</span>
            </button>
            <button
              onClick={onNavigateToReturns}
              className="flex items-center gap-2 px-5 py-3 rounded-2xl bg-slate-950 border border-slate-800 hover:border-cyan-500/50 text-slate-200 hover:text-white font-semibold text-xs transition-all hover:scale-105 shadow-md"
            >
              <RotateCcw className="w-4 h-4 text-emerald-400" />
              <span>{t('returnsCounterBtn', currentLang)}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Voice & Query Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* Left Column: Voice Orb & Input Form */}
        <div className="lg:col-span-7 bg-slate-900/80 border border-slate-800 rounded-3xl p-6 lg:p-8 space-y-6 shadow-xl relative backdrop-blur-md">
          
          {/* Voice Wave Orb */}
          <VoiceWave
            isListening={isListening}
            isSpeaking={isSpeaking}
            isLoading={isLoading}
            onMicClick={handleMicToggle}
            hasSpeechRecognition={hasSpeechRecognition}
            currentLang={currentLang}
          />

          {/* Form Input */}
          <form 
            onSubmit={(e) => { e.preventDefault(); handleSendQuery(); }}
            className="relative flex items-center"
          >
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder={t('inputPlaceholder', currentLang)}
              disabled={isLoading}
              className="w-full bg-slate-950 border border-slate-800 focus:border-cyan-500 rounded-2xl pl-5 pr-14 py-4 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/20 shadow-inner font-medium transition-all"
            />
            <button
              type="submit"
              disabled={!inputText.trim() || isLoading}
              className="absolute right-2.5 p-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 disabled:opacity-40 text-white transition-all shadow-md"
            >
              {isLoading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            </button>
          </form>

          {/* Error Message Display */}
          {errorMessage && (
            <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-3">
              <AlertTriangle className="w-4 h-4 shrink-0 text-rose-400" />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* Suggested Prompts Grid */}
          <SuggestedPrompts
            currentLang={currentLang}
            onSelectPrompt={(promptText) => {
              setInputText(promptText);
              handleSendQuery(promptText);
            }} 
          />

        </div>

        {/* Right Column: AI Live Response & Product Cards */}
        <div className="lg:col-span-5 space-y-6">
          
          {latestResponse ? (
            <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 space-y-5 shadow-xl backdrop-blur-md animate-fadeIn">
              
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <div className="w-7 h-7 rounded-xl bg-cyan-500/20 text-cyan-400 flex items-center justify-center">
                    <Sparkles className="w-4 h-4" />
                  </div>
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
                    Assistant Answer
                  </span>
                </div>
                {latestResponse.isMock && (
                  <span className="text-[10px] bg-amber-500/10 text-amber-400 px-2 py-0.5 rounded-md border border-amber-500/20 font-mono">
                    RAG Mock
                  </span>
                )}
              </div>

              {/* Answer Text */}
              <div className="text-sm text-slate-200 leading-relaxed font-medium bg-slate-950/60 p-4 rounded-2xl border border-slate-800/80">
                {latestResponse.data.answer}
              </div>

              {/* Matched Products list */}
              {latestResponse.data.products && latestResponse.data.products.length > 0 && (
                <div className="space-y-3">
                  <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">
                    Matching Store Products ({latestResponse.data.products.length})
                  </span>
                  <div className="grid grid-cols-1 gap-4">
                    {latestResponse.data.products.map((p) => (
                      <ProductCard
                        key={p.id}
                        product={p}
                        currentLang={currentLang}
                        onLocateAisle={onLocateAisle}
                        onAskAboutProduct={(prod) => {
                          const q = `Check stock for ${prod.name}`;
                          setInputText(q);
                          handleSendQuery(q);
                        }}
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* Sources */}
              {latestResponse.data.sources && (
                <div className="pt-2 text-[11px] text-slate-500 font-mono flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" /> Source: {latestResponse.data.sources.join(', ')}
                </div>
              )}

            </div>
          ) : (
            <div className="bg-slate-900/50 border border-slate-800/80 rounded-3xl p-8 text-center space-y-4">
              <div className="w-16 h-16 rounded-2xl bg-cyan-500/10 text-cyan-400 flex items-center justify-center mx-auto border border-cyan-500/20">
                <Bot className="w-8 h-8" />
              </div>
              <h3 className="font-bold text-base text-slate-200">Ready to Assist</h3>
              <p className="text-xs text-slate-400 leading-relaxed max-w-xs mx-auto">
                Speak or select a question to see real-time inventory levels, store map coordinates, and product availability.
              </p>
            </div>
          )}

        </div>

      </div>

    </div>
  );
}
