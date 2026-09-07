import React, { useState, useEffect } from 'react';
import { MapPin, CheckCircle2, AlertTriangle, XCircle, Tag, ArrowRight } from 'lucide-react';
import { formatPrice } from '../config/apiConfig';
import { t } from '../services/i18n';

// Specific high-res images by Product ID
const PRODUCT_IMAGES = {
  P001: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=80", // Red Nike Air Max
  P002: "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=600&auto=format&fit=crop&q=80", // White Adidas Ultraboost
  P003: "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=600&auto=format&fit=crop&q=80", // Puma Sneaker
  P004: "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=600&auto=format&fit=crop&q=80", // Levi's Jeans
  P005: "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=600&auto=format&fit=crop&q=80", // Nike Dri-FIT T-Shirt
  P006: "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=600&auto=format&fit=crop&q=80", // Formal Shirt
  P007: "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&auto=format&fit=crop&q=80", // Galaxy Buds
  P008: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80", // Headphones
  P009: "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=600&auto=format&fit=crop&q=80", // Smartwatch
  P010: "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=80", // Leather Watch
  P011: "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=600&auto=format&fit=crop&q=80", // Sunglasses
  P012: "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600&auto=format&fit=crop&q=80", // Backpack
  P013: "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=600&auto=format&fit=crop&q=80", // Lamp
  P014: "https://images.unsplash.com/photo-1585670149967-b4f4da88cc9f?w=600&auto=format&fit=crop&q=80", // Kettle
};

// Category level fallback images
const CATEGORY_IMAGES = {
  shoes: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=80",
  footwear: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=80",
  clothing: "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=600&auto=format&fit=crop&q=80",
  apparel: "https://images.unsplash.com/photo-1548883354-7622d03aca27?w=600&auto=format&fit=crop&q=80",
  electronics: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80",
  accessories: "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=80",
  home: "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=600&auto=format&fit=crop&q=80",
};

// Guaranteed SVG Data URL fallback
const FALLBACK_SVG = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='600' height='400' viewBox='0 0 600 400'><rect width='100%' height='100%' fill='%230f172a'/><path d='M200 250 C240 210, 360 210, 400 250 L420 280 L180 280 Z' fill='%230284c7' opacity='0.8'/><circle cx='300' cy='180' r='45' fill='%2338bdf8'/><text x='50%' y='85%' font-size='20' font-weight='bold' fill='%2394a3b8' text-anchor='middle' font-family='sans-serif'>In-Store Product</text></svg>";

export default function ProductCard({ product, onLocateAisle, onAskAboutProduct, currentLang }) {
  const [hasImgError, setHasImgError] = useState(false);

  const pId = product ? (product.product_id || product.id || '').toUpperCase() : '';
  const pName = product ? product.name : '';

  useEffect(() => {
    setHasImgError(false);
  }, [pId, pName]);

  if (!product) return null;

  // Stock resolution
  const stockCount = typeof product.stock_quantity === 'number' 
    ? product.stock_quantity 
    : typeof product.stock === 'number' 
    ? product.stock 
    : 0;

  const isAvailable = product.in_stock !== undefined 
    ? Boolean(product.in_stock) 
    : stockCount > 0;

  // Primary Image Resolution
  const catKey = (product.category || '').toLowerCase();
  
  const resolvedImage = (product.image && product.image.trim()) 
    ? product.image 
    : (product.image_url && product.image_url.trim()) 
    ? product.image_url 
    : PRODUCT_IMAGES[pId] || CATEGORY_IMAGES[catKey] || CATEGORY_IMAGES.shoes;

  const currentImage = hasImgError ? FALLBACK_SVG : resolvedImage;

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
            src={currentImage}
            alt={product.name}
            referrerPolicy="no-referrer"
            onError={() => {
              if (!hasImgError) {
                setHasImgError(true);
              }
            }}
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
