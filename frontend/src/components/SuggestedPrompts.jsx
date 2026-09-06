import React from 'react';
import { HelpCircle, Sparkles, MapPin, PackageCheck, RotateCcw } from 'lucide-react';
import { t } from '../services/i18n';

export default function SuggestedPrompts({ onSelectPrompt, currentLang }) {
  const prompts = [
    {
      labelKey: "suggested1",
      categoryKey: "suggested1Cat",
      icon: PackageCheck,
      color: "from-cyan-500/10 to-blue-500/10 text-cyan-400 border-cyan-500/30"
    },
    {
      labelKey: "suggested2",
      categoryKey: "suggested2Cat",
      icon: MapPin,
      color: "from-purple-500/10 to-pink-500/10 text-purple-400 border-purple-500/30"
    },
    {
      labelKey: "suggested3",
      categoryKey: "suggested3Cat",
      icon: RotateCcw,
      color: "from-emerald-500/10 to-teal-500/10 text-emerald-400 border-emerald-500/30"
    },
    {
      labelKey: "suggested4",
      categoryKey: "suggested4Cat",
      icon: Sparkles,
      color: "from-amber-500/10 to-orange-500/10 text-amber-400 border-amber-500/30"
    }
  ];

  return (
    <div className="w-full">
      <div className="flex items-center gap-2 mb-3">
        <HelpCircle className="w-4 h-4 text-cyan-400" />
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          {t('suggestedTitle', currentLang)}
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {prompts.map((p, index) => {
          const Icon = p.icon;
          const labelText = t(p.labelKey, currentLang);
          const categoryText = t(p.categoryKey, currentLang);
          return (
            <button
              key={index}
              onClick={() => onSelectPrompt(labelText)}
              className={`flex items-start gap-3 p-3.5 rounded-2xl bg-gradient-to-r ${p.color} border hover:border-slate-600 transition-all hover:scale-[1.02] text-left group`}
            >
              <div className="p-2 rounded-xl bg-slate-950/60 shrink-0">
                <Icon className="w-4 h-4" />
              </div>
              <div>
                <span className="block text-[10px] uppercase font-bold tracking-wider opacity-70">
                  {categoryText}
                </span>
                <span className="block text-xs font-semibold text-slate-200 group-hover:text-white mt-0.5">
                  "{labelText}"
                </span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
