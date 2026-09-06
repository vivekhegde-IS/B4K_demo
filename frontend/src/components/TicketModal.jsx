import React from 'react';
import { X, CheckCircle2, QrCode, Printer, ShieldCheck, Copy } from 'lucide-react';
import { formatPrice } from '../config/apiConfig';
import { t } from '../services/i18n';

export default function TicketModal({ isOpen, onClose, ticketData, currentLang }) {
  if (!isOpen || !ticketData) return null;

  const handleCopyTicket = () => {
    if (ticketData.ticket_id) {
      navigator.clipboard.writeText(ticketData.ticket_id);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md animate-fadeIn">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 lg:p-8 max-w-md w-full shadow-2xl relative overflow-hidden text-center">
        
        {/* Header Badges */}
        <div className="flex justify-between items-center mb-4">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold uppercase tracking-wider">
            <ShieldCheck className="w-4 h-4" /> {t('verifiedTicket', currentLang)}
          </span>
          <button 
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white rounded-xl hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Success Icon */}
        <div className="w-16 h-16 rounded-full bg-gradient-to-tr from-emerald-500 to-teal-500 text-slate-950 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-emerald-500/30 animate-bounce">
          <CheckCircle2 className="w-10 h-10" />
        </div>

        <h3 className="font-extrabold text-xl text-white">
          {ticketData.action === 'exchange' ? t('exchangeCreated', currentLang) : t('returnApproved', currentLang)}
        </h3>
        <p className="text-xs text-slate-400 mt-1 max-w-xs mx-auto">
          {ticketData.message}
        </p>

        {/* Ticket Box */}
        <div className="my-6 p-5 rounded-2xl bg-slate-950 border border-slate-800 space-y-4 relative">
          
          {/* Ticket ID Bar */}
          <div className="flex items-center justify-between p-3 rounded-xl bg-slate-900 border border-slate-800">
            <div>
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold text-left">
                {t('ticketRef', currentLang)}
              </span>
              <span className="font-mono text-base font-extrabold text-cyan-400">
                {ticketData.ticket_id || 'RM-TCK-89421'}
              </span>
            </div>
            <button
              onClick={handleCopyTicket}
              title="Copy Ticket ID"
              className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
            >
              <Copy className="w-4 h-4" />
            </button>
          </div>

          {/* QR Code Mockup */}
          <div className="p-4 bg-white rounded-2xl w-36 h-36 mx-auto flex flex-col items-center justify-center shadow-inner">
            <QrCode className="w-28 h-28 text-slate-950" />
          </div>
          <span className="text-[10px] text-slate-400 uppercase tracking-widest block font-mono">
            {t('scanAtCounter', currentLang)}
          </span>

          {/* Details */}
          <div className="pt-2 border-t border-slate-800/80 text-left text-xs space-y-1.5">
            <div className="flex justify-between text-slate-400">
              <span>Order Ref:</span>
              <span className="font-semibold text-slate-200">{ticketData.order_id}</span>
            </div>
            {ticketData.amount && (
              <div className="flex justify-between text-slate-400">
                <span>{t('refundValue', currentLang)}</span>
                <span className="font-bold text-emerald-400">{formatPrice(Number(ticketData.amount))}</span>
              </div>
            )}
            <div className="flex justify-between text-slate-400">
              <span>Status:</span>
              <span className="font-bold text-cyan-400 uppercase">{ticketData.status || 'APPROVED'}</span>
            </div>
          </div>

        </div>

        {/* Buttons */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => window.print()}
            className="flex-1 py-3 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs transition-all flex items-center justify-center gap-2 border border-slate-700"
          >
            <Printer className="w-4 h-4" /> {t('printTicket', currentLang)}
          </button>
          <button
            onClick={onClose}
            className="flex-1 py-3 px-4 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold text-xs transition-all shadow-lg shadow-cyan-500/25"
          >
            {t('doneBtn', currentLang)}
          </button>
        </div>

      </div>
    </div>
  );
}
