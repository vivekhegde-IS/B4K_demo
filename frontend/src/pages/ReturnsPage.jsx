import React, { useState } from 'react';
import { 
  RotateCcw, 
  Search, 
  CheckCircle2, 
  XCircle, 
  RefreshCw, 
  Calendar, 
  QrCode,
  PackageCheck
} from 'lucide-react';
import { MOCK_ORDERS } from '../services/mockData';
import { initiateReturn } from '../services/api';
import TicketModal from '../components/TicketModal';
import { formatPrice } from '../config/apiConfig';
import { t } from '../services/i18n';

export default function ReturnsPage({ currentLang }) {
  const [orderInput, setOrderInput] = useState('ORD001');
  const [activeOrder, setActiveOrder] = useState(MOCK_ORDERS['ORD001']);
  const [actionChoice, setActionChoice] = useState('return'); // return | exchange
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [ticketData, setTicketData] = useState(null);
  const [isTicketOpen, setIsTicketOpen] = useState(false);
  const [searchError, setSearchError] = useState(null);

  const handleLookupOrder = (orderIdToSearch) => {
    const target = (orderIdToSearch || orderInput).trim().toUpperCase();
    setSearchError(null);
    if (!target) return;

    if (MOCK_ORDERS[target]) {
      setActiveOrder(MOCK_ORDERS[target]);
    } else {
      setActiveOrder(null);
      setSearchError(`Order '${target}' was not found. Try sample orders: ORD001, ORD002, or ORD003.`);
    }
  };

  const handleInitiateProcess = async () => {
    if (!activeOrder || isSubmitting) return;

    setIsSubmitting(true);

    try {
      // Calls POST /api/returns/initiate with payload { order_id, action }
      const res = await initiateReturn(activeOrder.order_id, actionChoice);
      setIsSubmitting(false);

      if (res && res.data) {
        setTicketData(res.data);
        setIsTicketOpen(true);
      }
    } catch (err) {
      console.error("Return initiation failed:", err);
      setIsSubmitting(false);
      setSearchError("Failed to initiate return request. Please try again.");
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-fadeIn pb-12">
      
      {/* Ticket Modal Pop-up */}
      <TicketModal
        isOpen={isTicketOpen}
        onClose={() => setIsTicketOpen(false)}
        ticketData={ticketData}
        currentLang={currentLang}
      />

      {/* Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 border border-slate-800 rounded-3xl p-6 lg:p-8 shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold">
            <RotateCcw className="w-3.5 h-3.5" /> {t('navReturns', currentLang)}
          </div>
          <h2 className="text-3xl font-extrabold text-white">
            {t('returnsTitle', currentLang)}
          </h2>
          <p className="text-xs text-slate-300 max-w-xl leading-relaxed">
            {t('returnsSubtitle', currentLang)}
          </p>
        </div>
      </div>

      {/* Order Lookup Controls */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 lg:p-8 space-y-6 shadow-xl backdrop-blur-md">
        
        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
            {t('orderInputLabel', currentLang)}
          </label>
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <input
                type="text"
                value={orderInput}
                onChange={(e) => setOrderInput(e.target.value.toUpperCase())}
                placeholder="e.g. ORD001"
                className="w-full bg-slate-950 border border-slate-800 focus:border-cyan-500 rounded-2xl px-5 py-3.5 text-base font-mono font-bold text-slate-100 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-cyan-500/20"
              />
            </div>
            <button
              onClick={() => handleLookupOrder()}
              className="px-6 py-3.5 rounded-2xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold text-sm transition-all shadow-lg shadow-cyan-500/20 flex items-center justify-center gap-2"
            >
              <Search className="w-4 h-4" /> {t('lookupOrderBtn', currentLang)}
            </button>
          </div>
        </div>

        {/* Demo Preset Orders Quick Bar */}
        <div className="flex items-center gap-2 pt-1">
          <span className="text-xs text-slate-400 font-medium">{t('quickReceipts', currentLang)}</span>
          {['ORD001', 'ORD002', 'ORD003'].map((code) => (
            <button
              key={code}
              onClick={() => { setOrderInput(code); handleLookupOrder(code); }}
              className={`px-3 py-1 rounded-xl text-xs font-mono font-bold transition-all border ${
                orderInput === code
                  ? 'bg-cyan-500/20 border-cyan-500 text-cyan-300'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              {code}
            </button>
          ))}
        </div>

        {searchError && (
          <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
            <XCircle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{searchError}</span>
          </div>
        )}

      </div>

      {/* Order Details & Return Eligibility View */}
      {activeOrder && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 lg:p-8 space-y-6 shadow-xl backdrop-blur-md animate-fadeIn">
          
          {/* Top Order Status Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
            <div>
              <span className="text-xs text-slate-400 font-mono">Order Reference</span>
              <h3 className="font-extrabold text-xl text-white font-mono">{activeOrder.order_id}</h3>
              <span className="text-xs text-slate-400 flex items-center gap-1 mt-1">
                <Calendar className="w-3.5 h-3.5 text-cyan-400" /> Purchased: {activeOrder.date}
              </span>
            </div>

            {/* Eligibility Badge */}
            <div>
              {activeOrder.eligible_for_return ? (
                <div className="p-3 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
                  <div>
                    <span className="block font-bold">{t('eligibleBadge', currentLang)}</span>
                    <span className="text-[10px] text-emerald-400/80 font-normal">
                      {activeOrder.days_left} days remaining in window
                    </span>
                  </div>
                </div>
              ) : (
                <div className="p-3 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-bold flex items-center gap-2">
                  <XCircle className="w-5 h-5 text-rose-400 shrink-0" />
                  <div>
                    <span className="block font-bold">{t('ineligibleBadge', currentLang)}</span>
                    <span className="text-[10px] text-rose-400/80 font-normal">
                      {activeOrder.reason_ineligible || '30-day window expired'}
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Purchased Items List */}
          <div className="space-y-3">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block">
              {t('orderItemsHeader', currentLang)} ({activeOrder.items.length})
            </span>
            {activeOrder.items.map((item, idx) => (
              <div 
                key={idx}
                className="flex items-center justify-between p-4 rounded-2xl bg-slate-950 border border-slate-800 gap-4"
              >
                <div className="flex items-center gap-4">
                  <img
                    src={item.image}
                    alt={item.name}
                    className="w-16 h-16 rounded-xl object-cover border border-slate-800 shrink-0"
                  />
                  <div>
                    <h4 className="font-bold text-sm text-white">{item.name}</h4>
                    <p className="text-xs text-slate-400">
                      Size: <strong className="text-slate-200">{item.size}</strong> | Color: <strong className="text-slate-200">{item.color}</strong>
                    </p>
                    <span className="text-[10px] text-slate-500 font-mono">SKU: {item.sku}</span>
                  </div>
                </div>

                <div className="text-right">
                  <span className="font-extrabold text-base text-white">{formatPrice(item.price)}</span>
                  <span className="block text-[11px] text-slate-500 font-medium">Qty: {item.quantity}</span>
                </div>
              </div>
            ))}
          </div>

          {/* Action Choice: Return vs Exchange */}
          {activeOrder.eligible_for_return && (
            <div className="space-y-4 pt-4 border-t border-slate-800">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-300 block">
                {t('actionChoiceTitle', currentLang)}
              </span>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <button
                  type="button"
                  onClick={() => setActionChoice('return')}
                  className={`p-4 rounded-2xl border flex items-center gap-3 transition-all ${
                    actionChoice === 'return'
                      ? 'bg-cyan-500/10 border-cyan-500 ring-2 ring-cyan-500/30 text-white'
                      : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-white'
                  }`}
                >
                  <div className={`p-2.5 rounded-xl ${actionChoice === 'return' ? 'bg-cyan-500 text-slate-950' : 'bg-slate-900 text-slate-400'}`}>
                    <RotateCcw className="w-5 h-5" />
                  </div>
                  <div className="text-left">
                    <span className="block font-bold text-sm">{t('fullRefundReturn', currentLang)}</span>
                    <span className="text-[11px] text-slate-400">{t('fullRefundDesc', currentLang)} ({formatPrice(activeOrder.total)})</span>
                  </div>
                </button>

                <button
                  type="button"
                  onClick={() => setActionChoice('exchange')}
                  className={`p-4 rounded-2xl border flex items-center gap-3 transition-all ${
                    actionChoice === 'exchange'
                      ? 'bg-cyan-500/10 border-cyan-500 ring-2 ring-cyan-500/30 text-white'
                      : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-white'
                  }`}
                >
                  <div className={`p-2.5 rounded-xl ${actionChoice === 'exchange' ? 'bg-cyan-500 text-slate-950' : 'bg-slate-900 text-slate-400'}`}>
                    <PackageCheck className="w-5 h-5" />
                  </div>
                  <div className="text-left">
                    <span className="block font-bold text-sm">{t('sizeExchange', currentLang)}</span>
                    <span className="text-[11px] text-slate-400">{t('sizeExchangeDesc', currentLang)}</span>
                  </div>
                </button>
              </div>

              {/* Submit Button (Calls POST /api/returns/initiate) */}
              <div className="pt-4 flex justify-end">
                <button
                  onClick={handleInitiateProcess}
                  disabled={isSubmitting}
                  className="w-full sm:w-auto px-8 py-4 rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-extrabold text-sm transition-all shadow-lg shadow-emerald-500/25 flex items-center justify-center gap-2"
                >
                  {isSubmitting ? (
                    <>
                      <RefreshCw className="w-5 h-5 animate-spin" />
                      <span>Initiating API Request...</span>
                    </>
                  ) : (
                    <>
                      <QrCode className="w-5 h-5" />
                      <span>{t('initiateTicketBtn', currentLang)}</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          )}

        </div>
      )}

    </div>
  );
}
