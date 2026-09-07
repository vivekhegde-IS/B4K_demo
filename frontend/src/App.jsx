import React, { useState } from 'react';

import Header from './components/Header';

import ApiSettingsModal from './components/ApiSettingsModal';

import AisleMapModal from './components/AisleMapModal';

import KioskHome from './pages/KioskHome';

import InventoryPage from './pages/InventoryPage';

import ReturnsPage from './pages/ReturnsPage';

import ChatPage from './pages/ChatPage';

import {
  MessageSquare,
  Bot,
  Package,
  RotateCcw,
} from 'lucide-react';

import {
  getStoredLanguage,
  setStoredLanguage,
  t,
} from './services/i18n';

export default function App() {
  const [activeTab, setActiveTab] = useState('kiosk');

  const [isSettingsOpen, setIsSettingsOpen] =
    useState(false);

  const [voiceEnabled, setVoiceEnabled] =
    useState(true);

  const [currentLang, setCurrentLang] =
    useState(getStoredLanguage());

  /*
   * ---------------------------------------------------------
   * LANGUAGE CHANGE
   * ---------------------------------------------------------
   *
   * English -> en
   * Hindi   -> hi
   * Kannada -> kn
   *
   * We also save the selected language so it survives
   * a page refresh.
   */
  const handleLanguageChange = (langCode) => {
    console.log(
      '[RetailMate] Language changed to:',
      langCode
    );

    setCurrentLang(langCode);

    setStoredLanguage(langCode);
  };

  /*
   * ---------------------------------------------------------
   * AISLE MAP MODAL
   * ---------------------------------------------------------
   */

  const [mapModalProduct, setMapModalProduct] =
    useState(null);

  const [isMapModalOpen, setIsMapModalOpen] =
    useState(false);

  /*
   * ---------------------------------------------------------
   * GLOBAL CHAT TIMELINE
   * ---------------------------------------------------------
   */

  const [chatMessages, setChatMessages] = useState([
    {
      sender: 'ai',

      text:
        'Welcome to RetailMate Kiosk! I am your in-store RAG assistant. Ask me about stock in your size, aisle locations, or return policies.',

      time:
        new Date().toLocaleTimeString(),

      sources: [
        'RetailMate Store AI Engine',
      ],
    },
  ]);

  /*
   * ---------------------------------------------------------
   * ADD CHAT MESSAGE
   * ---------------------------------------------------------
   */

  const handleAddChatMessage = (msg) => {
    setChatMessages((prev) => [
      ...prev,
      msg,
    ]);
  };

  /*
   * ---------------------------------------------------------
   * CLEAR CHAT
   * ---------------------------------------------------------
   */

  const handleClearChat = () => {
    setChatMessages([]);
  };

  /*
   * ---------------------------------------------------------
   * OPEN AISLE MAP
   * ---------------------------------------------------------
   */

  const handleOpenAisleMap = (product) => {
    setMapModalProduct(product);

    setIsMapModalOpen(true);
  };

  /*
   * ---------------------------------------------------------
   * RESET KIOSK
   * ---------------------------------------------------------
   */

  const handleResetKiosk = () => {
    setActiveTab('kiosk');

    setChatMessages([
      {
        sender: 'ai',

        text:
          'Kiosk session reset. Welcome back! How can I assist you today?',

        time:
          new Date().toLocaleTimeString(),
      },
    ]);
  };

  /*
   * ---------------------------------------------------------
   * RENDER
   * ---------------------------------------------------------
   */

  return (
    <div
      className="
        min-h-screen
        bg-slate-950
        text-slate-100
        flex
        flex-col
        font-sans
        selection:bg-cyan-500
        selection:text-white
      "
    >

      {/* =====================================================
          TOP HEADER NAVIGATION
          ===================================================== */}

      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenSettings={() =>
          setIsSettingsOpen(true)
        }
        voiceEnabled={voiceEnabled}
        setVoiceEnabled={setVoiceEnabled}
        onResetKiosk={handleResetKiosk}
        currentLang={currentLang}
        onLanguageChange={handleLanguageChange}
      />

      {/* =====================================================
          MAIN CONTENT
          ===================================================== */}

      <main
        className="
          flex-1
          px-4
          lg:px-8
          py-6
          max-w-7xl
          mx-auto
          w-full
        "
      >

        {/* ===================================================
            KIOSK
            =================================================== */}

        {activeTab === 'kiosk' && (
          <KioskHome
            onNavigateToReturns={() =>
              setActiveTab('returns')
            }

            onNavigateToInventory={() =>
              setActiveTab('inventory')
            }

            onLocateAisle={
              handleOpenAisleMap
            }

            voiceEnabled={
              voiceEnabled
            }

            onAddChatMessage={
              handleAddChatMessage
            }

            currentLang={
              currentLang
            }
          />
        )}

        {/* ===================================================
            INVENTORY
            =================================================== */}

        {activeTab === 'inventory' && (
          <InventoryPage
            onLocateAisle={
              handleOpenAisleMap
            }

            currentLang={
              currentLang
            }

            onAskAboutProduct={(
              product
            ) => {
              setActiveTab('kiosk');
            }}
          />
        )}

        {/* ===================================================
            RETURNS
            =================================================== */}

        {activeTab === 'returns' && (
          <ReturnsPage
            currentLang={
              currentLang
            }
          />
        )}

        {/* ===================================================
            CHAT
            =================================================== */}

        {activeTab === 'chat' && (
          <ChatPage
            messages={
              chatMessages
            }

            onAddChatMessage={
              handleAddChatMessage
            }

            onClearChat={
              handleClearChat
            }

            onLocateAisle={
              handleOpenAisleMap
            }

            voiceEnabled={
              voiceEnabled
            }

            currentLang={
              currentLang
            }
          />
        )}

      </main>

      {/* =====================================================
          FLOATING BOTTOM QUICK TAB BAR
          ===================================================== */}

      <div
        className="
          fixed
          bottom-4
          left-1/2
          -translate-x-1/2
          z-30
          bg-slate-900/90
          border
          border-slate-800
          backdrop-blur-xl
          p-2
          rounded-2xl
          shadow-2xl
          flex
          items-center
          gap-2
        "
      >

        {/* ASSISTANT */}

        <button
          onClick={() =>
            setActiveTab('kiosk')
          }

          className={`
            flex
            items-center
            gap-1.5
            px-4
            py-2
            rounded-xl
            text-xs
            font-bold
            transition-all
            ${
              activeTab === 'kiosk'
                ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20'
                : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }
          `}
        >

          <Bot className="w-4 h-4" />

          {t(
            'navAssistant',
            currentLang
          )}

        </button>

        {/* PRODUCTS */}

        <button
          onClick={() =>
            setActiveTab('inventory')
          }

          className={`
            flex
            items-center
            gap-1.5
            px-4
            py-2
            rounded-xl
            text-xs
            font-bold
            transition-all
            ${
              activeTab === 'inventory'
                ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20'
                : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }
          `}
        >

          <Package className="w-4 h-4" />

          {t(
            'navProducts',
            currentLang
          )}

        </button>

        {/* RETURNS */}

        <button
          onClick={() =>
            setActiveTab('returns')
          }

          className={`
            flex
            items-center
            gap-1.5
            px-4
            py-2
            rounded-xl
            text-xs
            font-bold
            transition-all
            ${
              activeTab === 'returns'
                ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20'
                : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }
          `}
        >

          <RotateCcw className="w-4 h-4" />

          {t(
            'navReturns',
            currentLang
          )}

        </button>

        {/* CHAT */}

        <button
          onClick={() =>
            setActiveTab('chat')
          }

          className={`
            flex
            items-center
            gap-1.5
            px-4
            py-2
            rounded-xl
            text-xs
            font-bold
            transition-all
            ${
              activeTab === 'chat'
                ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20'
                : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }
          `}
        >

          <MessageSquare className="w-4 h-4" />

          {t(
            'navTimeline',
            currentLang
          )}

          ({chatMessages.length})

        </button>

      </div>

      {/* =====================================================
          GLOBAL MODALS
          ===================================================== */}

      <ApiSettingsModal
        isOpen={
          isSettingsOpen
        }

        onClose={() =>
          setIsSettingsOpen(false)
        }
      />

      <AisleMapModal
        isOpen={
          isMapModalOpen
        }

        onClose={() =>
          setIsMapModalOpen(false)
        }

        product={
          mapModalProduct
        }

        currentLang={
          currentLang
        }
      />

    </div>
  );
}