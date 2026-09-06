import React, { useState } from 'react';
import { Search, Filter, Package } from 'lucide-react';
import ProductCard from '../components/ProductCard';
import { MOCK_PRODUCTS } from '../services/mockData';
import { t } from '../services/i18n';

export default function InventoryPage({ onLocateAisle, onAskAboutProduct, currentLang }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [stockFilter, setStockFilter] = useState('all'); // all | instock | lowstock

  const categories = ['All', 'Footwear', 'Apparel', 'Electronics', 'Accessories'];

  const filteredProducts = MOCK_PRODUCTS.filter(p => {
    // Search query check
    const matchesSearch = 
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.aisle.toLowerCase().includes(searchQuery.toLowerCase());

    // Category check
    const matchesCategory = selectedCategory === 'All' || p.category === selectedCategory;

    // Stock check
    let matchesStock = true;
    if (stockFilter === 'instock') matchesStock = p.in_stock && p.stock > 0;
    if (stockFilter === 'lowstock') matchesStock = p.in_stock && p.stock <= 5 && p.stock > 0;

    return matchesSearch && matchesCategory && matchesStock;
  });

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-fadeIn pb-12">
      
      {/* Page Title Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/80 border border-slate-800 rounded-3xl p-6 lg:p-8 backdrop-blur-md">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-semibold mb-2">
            <Package className="w-3.5 h-3.5" /> {t('navProducts', currentLang)}
          </div>
          <h2 className="text-2xl lg:text-3xl font-extrabold text-white">
            {t('inventoryTitle', currentLang)}
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            {t('inventorySubtitle', currentLang)}
          </p>
        </div>

        {/* Live Search Input */}
        <div className="relative min-w-[280px]">
          <Search className="w-4 h-4 text-slate-400 absolute left-4 top-3.5" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={t('searchPlaceholder', currentLang)}
            className="w-full bg-slate-950 border border-slate-800 focus:border-cyan-500 rounded-2xl pl-11 pr-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/20"
          />
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-slate-950/60 p-4 rounded-2xl border border-slate-800">
        
        {/* Category Tabs */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 sm:pb-0">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                selectedCategory === cat
                  ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20 font-bold'
                  : 'bg-slate-900 text-slate-400 hover:text-white hover:bg-slate-800 border border-slate-800'
              }`}
            >
              {cat === 'All' ? t('allCategories', currentLang) : cat}
            </button>
          ))}
        </div>

        {/* Stock Filter Pills */}
        <div className="flex items-center gap-2">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          <select
            value={stockFilter}
            onChange={(e) => setStockFilter(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-cyan-500 font-medium"
          >
            <option value="all">{t('allAvailability', currentLang)}</option>
            <option value="instock">{t('inStockOnly', currentLang)}</option>
            <option value="lowstock">{t('lowStockOnly', currentLang)}</option>
          </select>
        </div>

      </div>

      {/* Product Cards Grid */}
      {filteredProducts.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProducts.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              currentLang={currentLang}
              onLocateAisle={onLocateAisle}
              onAskAboutProduct={onAskAboutProduct}
            />
          ))}
        </div>
      ) : (
        <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-12 text-center space-y-3">
          <Package className="w-10 h-10 text-slate-600 mx-auto" />
          <h3 className="font-bold text-slate-300 text-base">No Products Found</h3>
          <p className="text-xs text-slate-500">
            No items matched your search query "{searchQuery}". Try searching another name or reset filters.
          </p>
          <button
            onClick={() => { setSearchQuery(''); setSelectedCategory('All'); setStockFilter('all'); }}
            className="mt-2 text-xs font-semibold text-cyan-400 hover:underline"
          >
            Clear all filters
          </button>
        </div>
      )}

    </div>
  );
}
