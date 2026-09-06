import React, { useState, useEffect } from 'react';
import { X, Server, Check, AlertCircle, RefreshCw, Layers, DollarSign } from 'lucide-react';
import { getApiBaseUrl, setApiBaseUrl, isMockModeForced, setForceMockMode, DEFAULT_API_BASE_URL, getCurrency, setCurrency } from '../config/apiConfig';

export default function ApiSettingsModal({ isOpen, onClose }) {
  const [urlInput, setUrlInput] = useState('');
  const [forceMock, setForceMock] = useState(false);
  const [currencyChoice, setCurrencyChoice] = useState('INR');
  const [testingStatus, setTestingStatus] = useState('idle'); // idle | testing | success | error
  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setUrlInput(getApiBaseUrl());
      setForceMock(isMockModeForced());
      setCurrencyChoice(getCurrency());
      setTestingStatus('idle');
      setSavedSuccess(false);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSave = () => {
    setApiBaseUrl(urlInput);
    setForceMockMode(forceMock);
    setCurrency(currencyChoice);
    setSavedSuccess(true);
    setTimeout(() => {
      setSavedSuccess(false);
      window.location.reload(); // reload to apply currency changes across app
    }, 600);
  };

  const handleTestConnection = async () => {
    setTestingStatus('testing');
    try {
      const clean = urlInput.trim().replace(/\/$/, '');
      const response = await fetch(`${clean}/docs`, { method: 'HEAD', mode: 'no-cors' });
      // standard ping
      setTestingStatus('success');
    } catch (err) {
      console.warn('API ping error:', err);
      setTestingStatus('error');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 lg:p-8 max-w-md w-full shadow-2xl relative overflow-hidden">
        
        {/* Ambient Top Glow */}
        <div className="absolute -top-12 -right-12 w-40 h-40 bg-cyan-500/20 rounded-full blur-3xl pointer-events-none" />

        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center">
              <Server className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-lg text-white">Backend API Settings</h3>
              <p className="text-xs text-slate-400">Configure FastAPI Server Connection</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white rounded-xl hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="py-5 space-y-5">
          {/* Base URL Input */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              FastAPI Base URL
            </label>
            <div className="relative">
              <input
                type="url"
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                placeholder="http://localhost:8000"
                className="w-full bg-slate-950 border border-slate-800 focus:border-cyan-500 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-cyan-500/20 font-mono"
              />
              <button
                onClick={() => setUrlInput(DEFAULT_API_BASE_URL)}
                className="absolute right-2 top-2 text-[10px] uppercase tracking-wider font-semibold text-cyan-400 hover:text-cyan-300 bg-cyan-500/10 border border-cyan-500/20 px-2 py-1.5 rounded-lg"
              >
                Reset Default
              </button>
            </div>
            <p className="mt-1.5 text-[11px] text-slate-400">
              Expected endpoints: <code className="text-cyan-400 font-mono">POST /api/assistant/query</code> & <code className="text-cyan-400 font-mono">POST /api/returns/initiate</code>
            </p>
          </div>

          {/* Connection Test */}
          <div className="flex items-center justify-between p-3 bg-slate-950/60 rounded-2xl border border-slate-800">
            <div className="flex items-center gap-2">
              {testingStatus === 'testing' && <RefreshCw className="w-4 h-4 text-cyan-400 animate-spin" />}
              {testingStatus === 'success' && <Check className="w-4 h-4 text-emerald-400" />}
              {testingStatus === 'error' && <AlertCircle className="w-4 h-4 text-amber-400" />}
              {testingStatus === 'idle' && <Server className="w-4 h-4 text-slate-400" />}
              <span className="text-xs text-slate-300 font-medium">
                {testingStatus === 'testing' && 'Pinging endpoint...'}
                {testingStatus === 'success' && 'Connection reachable!'}
                {testingStatus === 'error' && 'Server offline or CORS blocked'}
                {testingStatus === 'idle' && 'Test backend connectivity'}
              </span>
            </div>
            <button
              onClick={handleTestConnection}
              disabled={testingStatus === 'testing'}
              className="text-xs font-semibold text-cyan-400 hover:text-cyan-300 bg-slate-900 border border-slate-800 hover:border-slate-700 px-3 py-1.5 rounded-xl transition-all"
            >
              Test Connection
            </button>
          </div>

          {/* Currency Preference Toggle */}
          <div className="flex items-center justify-between p-4 bg-slate-950/80 rounded-2xl border border-slate-800">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-xl bg-cyan-500/10 text-cyan-400 flex items-center justify-center font-extrabold text-base">
                ₹
              </div>
              <div>
                <span className="block text-sm font-semibold text-slate-200">Display Currency</span>
                <span className="block text-[11px] text-slate-400">Convert product prices & refunds</span>
              </div>
            </div>
            <div className="flex items-center gap-1 bg-slate-900 p-1 rounded-xl border border-slate-800">
              <button
                type="button"
                onClick={() => setCurrencyChoice('INR')}
                className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                  currencyChoice === 'INR'
                    ? 'bg-cyan-500 text-slate-950 shadow-md'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                INR (₹)
              </button>
              <button
                type="button"
                onClick={() => setCurrencyChoice('USD')}
                className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                  currencyChoice === 'USD'
                    ? 'bg-cyan-500 text-slate-950 shadow-md'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                USD ($)
              </button>
            </div>
          </div>

          {/* Force Mock Toggle */}
          <div className="flex items-center justify-between p-4 bg-slate-950/80 rounded-2xl border border-slate-800">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-xl bg-amber-500/10 text-amber-400 flex items-center justify-center">
                <Layers className="w-4 h-4" />
              </div>
              <div>
                <span className="block text-sm font-semibold text-slate-200">Force Standalone Demo Mode</span>
                <span className="block text-[11px] text-slate-400">Uses internal RAG engine & mock data offline</span>
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={forceMock}
                onChange={(e) => setForceMock(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-cyan-500"></div>
            </label>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
          <button
            onClick={onClose}
            className="px-4 py-2.5 rounded-xl text-sm font-medium text-slate-400 hover:text-white transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="px-6 py-2.5 rounded-xl text-sm font-semibold bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white shadow-lg shadow-cyan-500/25 transition-all flex items-center gap-2"
          >
            {savedSuccess ? (
              <>
                <Check className="w-4 h-4" /> Saved!
              </>
            ) : (
              'Save Settings'
            )}
          </button>
        </div>

      </div>
    </div>
  );
}
