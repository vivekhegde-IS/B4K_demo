import React from 'react';
import { MapPin, CheckCircle2, AlertTriangle, XCircle, Tag, ArrowRight } from 'lucide-react';
import { formatPrice } from '../config/apiConfig';
import { t } from '../services/i18n';

const CATEGORY_IMAGES = {
  shoes: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=80",
  footwear: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=80",
  clothing: "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=600&auto=format&fit=crop&q=80",
  apparel: "https://images.unsplash.com/photo-1548883354-7622d03aca27?w=600&auto=format&fit=crop&q=80",
  electronics: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80",
  accessories: "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=80",
  home: "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=600&auto=format&fit=crop&q=80",
};

export default function ProductCard({ product, onLocateAisle, onAskAboutProduct, currentLang }) {
  if (!product) return null;

  // Stock resolution
  const stockCount = typeof product.stock_quantity === 'number' 
    ? product.stock_quantity 
    : typeof product.stock === 'number' 
    ? product.stock 
    : 0;

  const isAvailable = product.in_stock !== undefined 
    ? product.in_stock 
    : stockCount > 0;

  // Image resolution
  const catKey = (product.category || '').toLowerCase();
  const defaultImg = CATEGORY_IMAGES[catKey] || "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=80";
  const imageUrl = (product.image && product.image.trim()) 
    ? product.image 
    : (product.image_url && product.image_url.trim()) 
    ? product.image_url 
    : defaultImg;

  // Location resolution
  let aisleText = product.aisle;
  let sectionText = product.section;

  if (!aisleText && product.location) {
    aisleText = typeof product.location === 'string' 
      ? product.location 
      : product.location.aisle 
      ? `Aisle ${product.location.aisle}` 
      : 'Main Aisle';
    
    if (product.location.shelf) {
      sectionText = `Shelf ${product.location.shelf}`;
    }
  }

  aisleText = aisleText || "Aisle 3 - Retail";
  sectionText = sectionText || "Section A";

  const getStockBadge = (stock, inStock) => {
    if (!inStock || stock === 0) {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-semibold">
          <XCircle className="w-3.5 h-3.5" /> {t('outOfStock', currentLang)}
        </span>
      );
    }
    if (stock <= 5) {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-semibold">
          <AlertTriangle className="w-3.5 h-3.5" /> {t('lowStock', currentLang)} ({stock} {t('unitsLeft', currentLang)})
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold">
        <CheckCircle2 className="w-3.5 h-3.5" /> {t('inStock', currentLang)} ({stock} {t('unitsAvailable', currentLang)})
      </span>
    );
  };

  return (
    <div className="group relative bg-slate-900/90 border border-slate-800 hover:border-cyan-500/40 rounded-3xl overflow-hidden transition-all duration-300 hover:shadow-xl hover:shadow-cyan-500/10 flex flex-col justify-between">
      
      <div>
        {/* Product Image & Badges */}
        <div className="relative h-44 w-full bg-slate-950 overflow-hidden">
          <img
            src={imageUrl}
            alt={product.name}
            onError={(e) => { e.target.src = defaultImg; }}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 opacity-90 group-hover:opacity-100"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-transparent to-transparent opacity-80" />

          {/* Top Category Badge */}
          <div className="absolute top-3 left-3">
            <span className="bg-slate-950/80 backdrop-blur-md text-slate-300 text-[10px] uppercase font-bold tracking-wider px-2.5 py-1 rounded-lg border border-slate-800">
              {product.category || 'General'}
            </span>
          </div>

          {/* Top Stock Badge */}
          <div className="absolute top-3 right-3">
            {getStockBadge(stockCount, isAvailable)}
          </div>
        </div>

        {/* Card Body */}
        <div className="p-5 space-y-3">
          <div className="flex items-start justify-between gap-2">
            <h4 className="font-bold text-base text-white group-hover:text-cyan-300 transition-colors line-clamp-1">
              {product.name}
            </h4>
          </div>

          <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
            {product.description || 'In-store retail item available for purchase.'}
          </p>

          {/* Price & SKU */}
          <div className="flex items-center justify-between pt-1">
            <div className="flex items-center gap-1.5">
              <Tag className="w-4 h-4 text-cyan-400" />
              <span className="font-extrabold text-xl text-white">
                {formatPrice(product.price)}
              </span>
            </div>

            {product.sizes && Array.isArray(product.sizes) && product.sizes.length > 0 && (
              <span className="text-[11px] text-slate-400 font-medium">
                Sizes: {product.sizes.slice(0, 3).join(', ')}{product.sizes.length > 3 ? '+' : ''}
              </span>
            )}
          </div>

          {/* Aisle Location Banner */}
          <div className="flex items-center justify-between p-3 rounded-2xl bg-cyan-950/40 border border-cyan-800/40 text-cyan-300 text-xs">
            <div className="flex items-center gap-2">
              <MapPin className="w-4 h-4 text-cyan-400 shrink-0" />
              <div>
                <span className="font-bold block">{aisleText}</span>
                <span className="text-[10px] text-cyan-400/80">{sectionText}</span>
              </div>
            </div>
            {onLocateAisle && (
              <button
                onClick={() => onLocateAisle({ ...product, aisle: aisleText, section: sectionText })}
                className="text-[11px] font-bold text-cyan-400 hover:text-cyan-200 underline underline-offset-2"
              >
                {t('viewMap', currentLang)}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Action Footer */}
      {onAskAboutProduct && (
        <div className="p-4 pt-0">
          <button
            onClick={() => onAskAboutProduct(product)}
            className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-cyan-600 text-slate-200 hover:text-white font-semibold text-xs transition-all border border-slate-700 hover:border-cyan-500"
          >
            <span>{t('askAssistantAboutItem', currentLang)}</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

    </div>
  );
}
