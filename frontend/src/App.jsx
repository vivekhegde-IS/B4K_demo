import React, { useState } from 'react';
import Header from './components/Header';
import ApiSettingsModal from './components/ApiSettingsModal';
import AisleMapModal from './components/AisleMapModal';
import KioskHome from './pages/KioskHome';
import InventoryPage from './pages/InventoryPage';
import ReturnsPage from './pages/ReturnsPage';
import ChatPage from './pages/ChatPage';
import { MessageSquare, Bot, Package, RotateCcw } from 'lucide-react';
import { getStoredLanguage, setStoredLanguage, t } from './services/i18n';

export default function App() {
  const [activeTab, setActiveTab] = useState('kiosk'); // kiosk | inventory | returns | chat
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [currentLang, setCurrentLang] = useState(getStoredLanguage());

  const handleLanguageChange = (langCode) => {
    setCurrentLang(langCode);
    setStoredLanguage(langCode);
  };
  
  // Aisle Map Modal State
  const [mapModalProduct, setMapModalProduct] = useState(null);
  const [isMapModalOpen, setIsMapModalOpen] = useState(false);

  // Global Chat Timeline Messages
  const [chatMessages, setChatMessages] = useState([
    {
      sender: 'ai',
      text: "Welcome to RetailMate Kiosk! I am your in-store RAG assistant. Ask me about stock in your size, aisle locations, or return policies.",
      time: new Date().toLocaleTimeString(),
      sources: ["RetailMate Store AI Engine"]
    }
  ]);

  const handleAddChatMessage = (msg) => {
    setChatMessages((prev) => [...prev, msg]);
  };

  const handleClearChat = () => {
    setChatMessages([]);
  };

  const handleOpenAisleMap = (product) => {
    setMapModalProduct(product);
    setIsMapModalOpen(true);
  };

  const handleResetKiosk = () => {
    setActiveTab('kiosk');
    setChatMessages([
      {
        sender: 'ai',
        text: "Kiosk session reset. Welcome back! How can I assist you today?",
        time: new Date().toLocaleTimeString()
      }
    ]);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-cyan-500 selection:text-white">
      
      {/* Top Header Navigation */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenSettings={() => setIsSettingsOpen(true)}
        voiceEnabled={voiceEnabled}
        setVoiceEnabled={setVoiceEnabled}
        onResetKiosk={handleResetKiosk}
        currentLang={currentLang}
        onLanguageChange={handleLanguageChange}
      />

      {/* Main Content View Container */}
      <main className="flex-1 px-4 lg:px-8 py-6 max-w-7xl mx-auto w-full">
        {activeTab === 'kiosk' && (
          <KioskHome
            onNavigateToReturns={() => setActiveTab('returns')}
            onNavigateToInventory={() => setActiveTab('inventory')}
            onLocateAisle={handleOpenAisleMap}
            voiceEnabled={voiceEnabled}
            onAddChatMessage={handleAddChatMessage}
            currentLang={currentLang}
          />
        )}

        {activeTab === 'inventory' && (
          <InventoryPage
            onLocateAisle={handleOpenAisleMap}
            currentLang={currentLang}
            onAskAboutProduct={(product) => {
              setActiveTab('kiosk');
            }}
          />
        )}

        {activeTab === 'returns' && (
          <ReturnsPage
            currentLang={currentLang}
          />
        )}

        {activeTab === 'chat' && (
          <ChatPage
            messages={chatMessages}
            onAddChatMessage={handleAddChatMessage}
            onClearChat={handleClearChat}
            onLocateAisle={handleOpenAisleMap}
            voiceEnabled={voiceEnabled}
            currentLang={currentLang}
          />
        )}
      </main>

      {/* Floating Bottom Quick Tab Bar for Touch Kiosk Accessibility */}
      <div className="fixed bottom-4 left-1/2 -translate-x-1/2 z-30 bg-slate-900/90 border border-slate-800 backdrop-blur-xl p-2 rounded-2xl shadow-2xl flex items-center gap-2">
        <button
          onClick={() => setActiveTab('kiosk')}
          className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === 'kiosk'
              ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          <Bot className="w-4 h-4" /> {t('navAssistant', currentLang)}
        </button>

        <button
          onClick={() => setActiveTab('inventory')}
          className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === 'inventory'
              ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          <Package className="w-4 h-4" /> {t('navProducts', currentLang)}
        </button>

        <button
          onClick={() => setActiveTab('returns')}
          className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === 'returns'
              ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          <RotateCcw className="w-4 h-4" /> {t('navReturns', currentLang)}
        </button>

        <button
          onClick={() => setActiveTab('chat')}
          className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === 'chat'
              ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          <MessageSquare className="w-4 h-4" /> {t('navTimeline', currentLang)} ({chatMessages.length})
        </button>
      </div>

      {/* Global Modals */}
      <ApiSettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
      />

      <AisleMapModal
        isOpen={isMapModalOpen}
        onClose={() => setIsMapModalOpen(false)}
        product={mapModalProduct}
        currentLang={currentLang}
      />

    </div>
  );
}
