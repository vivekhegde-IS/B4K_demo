import React from 'react';
import { X, MapPin, Navigation, Compass } from 'lucide-react';
import { t } from '../services/i18n';

export default function AisleMapModal({ isOpen, onClose, product, currentLang }) {
  if (!isOpen || !product) return null;

  const aisles = [
    { id: "Aisle 1 - Tech Kiosk", label: "Aisle 1: Electronics & Tech" },
    { id: "Aisle 3 - Footwear", label: "Aisle 3: Footwear & Shoes" },
    { id: "Aisle 5 - Outerwear", label: "Aisle 5: Apparel & Jackets" },
    { id: "Aisle 7 - Active Gear", label: "Aisle 7: Accessories & Bottles" },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md animate-fadeIn">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 lg:p-8 max-w-2xl w-full shadow-2xl relative overflow-hidden">
        
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center">
              <Navigation className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-lg text-white">{t('floorNavTitle', currentLang)}</h3>
              <p className="text-xs text-slate-400">{t('locating', currentLang)}: <span className="text-cyan-300 font-semibold">{product.name}</span></p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white rounded-xl hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Visual Map Canvas */}
        <div className="py-6 space-y-4">
          <div className="relative bg-slate-950 rounded-2xl p-6 border border-slate-800 overflow-hidden min-h-[260px] flex flex-col justify-between">
            
            {/* Grid Lines */}
            <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:2rem_2rem] opacity-30" />

            {/* Entrance Marker */}
            <div className="relative z-10 flex items-center justify-between">
              <span className="px-3 py-1 bg-slate-800 border border-slate-700 text-slate-300 rounded-lg text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">
                <Compass className="w-3.5 h-3.5 text-cyan-400" /> {t('youAreHere', currentLang)}
              </span>
              <span className="text-xs text-slate-500 font-mono">Store Floorplan Level 1</span>
            </div>

            {/* Aisles Graphic Grid */}
            <div className="relative z-10 grid grid-cols-2 sm:grid-cols-4 gap-3 my-6">
              {aisles.map((aisleItem) => {
                const isTarget = product.aisle.includes(aisleItem.id.split(' - ')[0]) || product.aisle === aisleItem.id;
                return (
                  <div
                    key={aisleItem.id}
                    className={`relative p-4 rounded-xl border flex flex-col items-center justify-center text-center transition-all ${
                      isTarget
                        ? 'bg-cyan-500/20 border-cyan-400 ring-2 ring-cyan-400/50 shadow-lg shadow-cyan-500/30 scale-105'
                        : 'bg-slate-900/80 border-slate-800 opacity-60'
                    }`}
                  >
                    {isTarget && (
                      <span className="absolute -top-3 px-2 py-0.5 rounded-full bg-cyan-400 text-slate-950 font-black text-[10px] uppercase tracking-wider animate-bounce">
                        {t('targetAisle', currentLang)}
                      </span>
                    )}

                    <MapPin className={`w-6 h-6 mb-1 ${isTarget ? 'text-cyan-300 animate-pulse' : 'text-slate-500'}`} />
                    <span className={`text-xs font-bold ${isTarget ? 'text-white' : 'text-slate-400'}`}>
                      {aisleItem.id.split(' - ')[0]}
                    </span>
                    <span className="text-[10px] text-slate-400 font-medium">
                      {aisleItem.id.split(' - ')[1]}
                    </span>
                  </div>
                );
              })}
            </div>

            {/* Bottom Guidance Info */}
            <div className="relative z-10 flex items-center justify-between p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs">
              <span className="text-slate-300 font-medium">
                📍 Location: <strong className="text-cyan-300">{product.aisle}</strong> — {product.section}
              </span>
              <span className="text-slate-400 text-[11px]">
                Approx. 35 feet from this kiosk
              </span>
            </div>

          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end pt-2">
          <button
            onClick={onClose}
            className="px-6 py-2.5 rounded-xl text-sm font-semibold bg-cyan-500 hover:bg-cyan-400 text-slate-950 transition-all shadow-lg shadow-cyan-500/20"
          >
            {t('gotIt', currentLang)}
          </button>
        </div>

      </div>
    </div>
  );
}
