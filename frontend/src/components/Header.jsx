import React, { useState, useEffect } from 'react';
import { 
  Store, 
  Settings, 
  Wifi, 
  Volume2, 
  VolumeX, 
  MapPin, 
  RotateCcw, 
  Search, 
  Sparkles,
  Bot,
  Globe
} from 'lucide-react';
import { getApiBaseUrl, isMockModeForced } from '../config/apiConfig';
import { LANGUAGES, t } from '../services/i18n';

export default function Header({ 
  activeTab, 
  setActiveTab, 
  onOpenSettings, 
  voiceEnabled, 
  setVoiceEnabled,
  onResetKiosk,
  currentLang,
  onLanguageChange
}) {
  const [timeStr, setTimeStr] = useState('');
  const [dateStr, setDateStr] = useState('');
  const [mockMode, setMockMode] = useState(false);

  useEffect(() => {
    setMockMode(isMockModeForced());

    const updateClock = () => {
      const now = new Date();
      setTimeStr(now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
      setDateStr(now.toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' }));
    };

    updateClock();
    const interval = setInterval(updateClock, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="sticky top-0 z-40 bg-slate-900/80 backdrop-blur-xl border-b border-slate-800 px-4 lg:px-8 py-3 transition-all">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        
        {/* Logo & Store Info */}
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-2xl bg-gradient-to-tr from-cyan-500 via-blue-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 text-white transform hover:scale-105 transition-transform">
            <Store className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-extrabold text-xl tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-100 to-slate-400">
                {t('brandName', currentLang)}
              </h1>
              <span className="bg-cyan-500/10 text-cyan-400 text-xs font-semibold px-2 py-0.5 rounded-full border border-cyan-500/20 flex items-center gap-1">
                <Sparkles className="w-3 h-3 animate-pulse" /> {t('kioskTitle', currentLang)}
              </span>
            </div>
            <p className="text-xs text-slate-400 flex items-center gap-1">
              <MapPin className="w-3 h-3 text-cyan-400" /> {t('storeLocation', currentLang)}
            </p>
          </div>
        </div>

        {/* Center Navigation Tabs */}
        <nav className="flex items-center bg-slate-950/70 p-1.5 rounded-2xl border border-slate-800 shadow-inner">
          <button
            onClick={() => setActiveTab('kiosk')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all ${
              activeTab === 'kiosk'
                ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-lg shadow-cyan-500/25'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <Bot className="w-4 h-4" />
            <span>{t('navAssistant', currentLang)}</span>
          </button>

          <button
            onClick={() => setActiveTab('inventory')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all ${
              activeTab === 'inventory'
                ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-lg shadow-cyan-500/25'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <Search className="w-4 h-4" />
            <span>{t('navProducts', currentLang)}</span>
          </button>

          <button
            onClick={() => setActiveTab('returns')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all ${
              activeTab === 'returns'
                ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-lg shadow-cyan-500/25'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <RotateCcw className="w-4 h-4" />
            <span>{t('navReturns', currentLang)}</span>
          </button>
        </nav>

        {/* Right Status Controls */}
        <div className="flex items-center gap-3">
          
          {/* Regional Language Selector */}
          <div className="flex items-center gap-1 bg-slate-950/80 p-1 rounded-2xl border border-slate-800">
            <Globe className="w-4 h-4 text-cyan-400 ml-1.5 shrink-0" />
            {LANGUAGES.map((lang) => (
              <button
                key={lang.code}
                onClick={() => onLanguageChange(lang.code)}
                title={`Switch language to ${lang.name}`}
                className={`px-2.5 py-1 rounded-xl text-xs font-bold transition-all ${
                  currentLang === lang.code
                    ? 'bg-cyan-500 text-slate-950 shadow-md'
                    : 'text-slate-400 hover:text-white hover:bg-slate-900'
                }`}
              >
                {lang.native}
              </button>
            ))}
          </div>

          {/* Clock */}
          <div className="hidden xl:flex flex-col items-end px-3 py-1 bg-slate-950/50 rounded-xl border border-slate-800 text-right">
            <span className="font-mono text-sm font-bold text-slate-200">{timeStr}</span>
            <span className="text-[10px] uppercase tracking-wider text-slate-400 font-medium">{dateStr}</span>
          </div>

          {/* Voice Output Toggle */}
          <button
            onClick={() => setVoiceEnabled(!voiceEnabled)}
            title={voiceEnabled ? "Voice Output Active" : "Voice Output Muted"}
            className={`p-2.5 rounded-xl border transition-all ${
              voiceEnabled 
                ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/20' 
                : 'bg-slate-800 border-slate-700 text-slate-400 hover:bg-slate-700'
            }`}
          >
            {voiceEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
          </button>

          {/* API Connection Indicator */}
          <button
            onClick={onOpenSettings}
            className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-950/80 border border-slate-800 hover:border-slate-700 text-xs font-medium text-slate-300 transition-all hover:bg-slate-900 group"
          >
            <span className="relative flex h-2 w-2">
              <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                mockMode ? 'bg-amber-400' : 'bg-emerald-400'
              }`}></span>
              <span className={`relative inline-flex rounded-full h-2 w-2 ${
                mockMode ? 'bg-amber-500' : 'bg-emerald-500'
              }`}></span>
            </span>
            <span className="hidden sm:inline">
              {mockMode ? t('demoMode', currentLang) : t('fastapiReady', currentLang)}
            </span>
            <Settings className="w-3.5 h-3.5 text-slate-400 group-hover:text-cyan-400 transition-colors ml-1" />
          </button>

          {/* Reset Kiosk Button */}
          <button
            onClick={onResetKiosk}
            title={t('resetKiosk', currentLang)}
            className="p-2.5 rounded-xl bg-slate-800 border border-slate-700 text-slate-400 hover:text-white hover:bg-slate-700 transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>

      </div>
    </header>
  );
}
