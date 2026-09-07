import React, { useState, useEffect } from 'react';
import { 
  PlusCircle, 
  Trash2, 
  PackagePlus, 
  CheckCircle2, 
  Plus, 
  Minus 
} from 'lucide-react';
import { 
  getInventoryProducts, 
  addInventoryItem, 
  deleteInventoryItem, 
  updateStockCount 
} from '../services/mockData';
import { formatPrice } from '../config/apiConfig';
import { t } from '../services/i18n';

export default function ManageInventoryPage({ currentLang }) {
  const [products, setProducts] = useState([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [successToast, setSuccessToast] = useState(null);

  // Form State
  const [formData, setFormData] = useState({
    name: '',
    category: 'Footwear',
    price: '',
    stock: '',
    aisle: 'Aisle 2 - Apparel',
    section: 'Shelf A1',
    sizes: 'S, M, L, XL',
    sku: '',
    description: '',
    image: ''
  });

  useEffect(() => {
    setProducts(getInventoryProducts());
  }, []);

  const handleAddProduct = (e) => {
    e.preventDefault();
    if (!formData.name || !formData.price || !formData.stock) return;

    const updated = addInventoryItem(formData);
    setProducts(updated);
    setFormData({
      name: '',
      category: 'Footwear',
      price: '',
      stock: '',
      aisle: 'Aisle 2 - Apparel',
      section: 'Shelf A1',
      sizes: 'S, M, L, XL',
      sku: '',
      description: '',
      image: ''
    });
    setShowAddModal(false);
    setSuccessToast("New product added & indexed into RAG Inventory!");
    setTimeout(() => setSuccessToast(null), 4000);
  };

  const handleDelete = (id) => {
    const updated = deleteInventoryItem(id);
    setProducts(updated);
  };

  const handleStockChange = (id, delta) => {
    const updated = updateStockCount(id, delta);
    setProducts(updated);
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-fadeIn pb-12">
      
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-4 bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 border border-slate-800 rounded-3xl p-6 lg:p-8 shadow-xl relative overflow-hidden">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-semibold">
            <PackagePlus className="w-3.5 h-3.5" /> Store Manager Portal
          </div>
          <h2 className="text-2xl lg:text-3xl font-extrabold text-white">
            Manage Store Inventory
          </h2>
          <p className="text-xs text-slate-300">
            Add new products, adjust stock levels, or update aisle coordinates. Items added here are dynamically indexed by the RAG AI assistant.
          </p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="px-6 py-3.5 rounded-2xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold text-xs shadow-lg shadow-cyan-500/20 transition-all flex items-center gap-2 shrink-0"
        >
          <PlusCircle className="w-4 h-4" /> Add New Inventory Item
        </button>
      </div>

      {successToast && (
        <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-bold flex items-center gap-2 animate-fadeIn">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>{successToast}</span>
        </div>
      )}

      {/* Inventory Items List */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 space-y-4 shadow-xl backdrop-blur-md">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <h3 className="font-bold text-sm text-slate-200">
            Current Store Products ({products.length})
          </h3>
          <span className="text-[11px] text-cyan-400 font-mono">Live RAG Synced</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {products.map((p) => (
            <div 
              key={p.id}
              className="p-4 rounded-2xl bg-slate-950 border border-slate-800/80 flex items-center justify-between gap-4 hover:border-slate-700 transition-all"
            >
              <div className="flex items-center gap-4">
                <img
                  src={p.image}
                  alt={p.name}
                  className="w-14 h-14 rounded-xl object-cover border border-slate-800 shrink-0"
                />
                <div>
                  <h4 className="font-bold text-sm text-white line-clamp-1">{p.name}</h4>
                  <span className="text-xs font-bold text-cyan-400">{formatPrice(p.price)}</span>
                  <span className="text-[10px] text-slate-400 block font-mono">
                    {p.aisle} • {p.section}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-3 shrink-0">
                {/* Stock Controls */}
                <div className="flex items-center gap-1 bg-slate-900 px-2 py-1 rounded-xl border border-slate-800">
                  <button
                    onClick={() => handleStockChange(p.id, -1)}
                    className="p-1 text-slate-400 hover:text-white"
                  >
                    <Minus className="w-3.5 h-3.5" />
                  </button>
                  <span className="text-xs font-bold text-slate-200 px-1 font-mono">{p.stock}</span>
                  <button
                    onClick={() => handleStockChange(p.id, 1)}
                    className="p-1 text-slate-400 hover:text-white"
                  >
                    <Plus className="w-3.5 h-3.5" />
                  </button>
                </div>

                <button
                  onClick={() => handleDelete(p.id)}
                  className="p-2 text-slate-500 hover:text-rose-400 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Add Item Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md animate-fadeIn">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 lg:p-8 max-w-lg w-full shadow-2xl relative">
            <h3 className="font-extrabold text-xl text-white mb-4 flex items-center gap-2">
              <PackagePlus className="w-5 h-5 text-cyan-400" /> Add New Inventory Item
            </h3>

            <form onSubmit={handleAddProduct} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase mb-1">Product Name</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g. Puma Velocity Nitro 3"
                  className="w-full bg-slate-950 border border-slate-800 focus:border-cyan-500 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-400 uppercase mb-1">Category</label>
                  <select
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 focus:border-cyan-500 rounded-xl px-3 py-2.5 text-sm text-slate-100 focus:outline-none"
                  >
                    <option value="Footwear">Footwear</option>
                    <option value="Apparel">Apparel</option>
                    <option value="Electronics">Electronics</option>
                    <option value="Accessories">Accessories</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-400 uppercase mb-1">Price ($ USD)</label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={formData.price}
                    onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                    placeholder="e.g. 119.99"
                    className="w-full bg-slate-950 border border-slate-800 focus:border-cyan-500 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-400 uppercase mb-1">Stock Units</label>
                  <input
                    type="number"
                    required
                    value={formData.stock}
                    onChange={(e) => setFormData({ ...formData, stock: e.target.value })}
                    placeholder="e.g. 15"
                    className="w-full bg-slate-950 border border-slate-800 focus:border-cyan-500 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-400 uppercase mb-1">Store Aisle</label>
                  <input
                    type="text"
                    value={formData.aisle}
                    onChange={(e) => setFormData({ ...formData, aisle: e.target.value })}
                    placeholder="e.g. Aisle 3 - Footwear"
                    className="w-full bg-slate-950 border border-slate-800 focus:border-cyan-500 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase mb-1">Image URL (Optional)</label>
                <input
                  type="url"
                  value={formData.image}
                  onChange={(e) => setFormData({ ...formData, image: e.target.value })}
                  placeholder="https://..."
                  className="w-full bg-slate-950 border border-slate-800 focus:border-cyan-500 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase mb-1">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Short product description..."
                  rows={2}
                  className="w-full bg-slate-950 border border-slate-800 focus:border-cyan-500 rounded-xl px-4 py-2 text-sm text-slate-100 placeholder-slate-600 focus:outline-none"
                />
              </div>

              <div className="flex justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 text-xs font-semibold text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-6 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs shadow-md"
                >
                  Save & Index Item
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
