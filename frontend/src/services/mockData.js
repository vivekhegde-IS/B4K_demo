import { generateOpenRouterCompletion } from './openRouterService';

// Base Inventory Dataset
const INITIAL_PRODUCTS = [
  {
    id: "prod_1",
    name: "Nike Air Zoom Pegasus 40",
    category: "Footwear",
    price: 129.99,
    stock: 18,
    sizes: ["7", "8", "8.5", "9", "9.5", "10", "11"],
    aisle: "Aisle 3 - Footwear",
    section: "Shelf B2",
    in_stock: true,
    sku: "NK-AZP-40-BL",
    rating: 4.8,
    image: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=80",
    description: "Responsive cushioning in the Pegasus provides an energized ride for everyday road running."
  },
  {
    id: "prod_2",
    name: "Adidas Ultraboost Light",
    category: "Footwear",
    price: 189.95,
    stock: 6,
    sizes: ["8", "9", "10", "11"],
    aisle: "Aisle 3 - Footwear",
    section: "Shelf C1",
    in_stock: true,
    sku: "AD-UBL-24",
    rating: 4.7,
    image: "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=600&auto=format&fit=crop&q=80",
    description: "Experience epic energy with the new Ultraboost Light, our lightest Ultraboost ever."
  },
  {
    id: "prod_3",
    name: "North Face ThermoBall Eco Jacket",
    category: "Apparel",
    price: 198.00,
    stock: 0,
    sizes: ["M", "L", "XL"],
    aisle: "Aisle 5 - Outerwear",
    section: "Rack 12",
    in_stock: false,
    sku: "TNF-TB-ECO",
    rating: 4.6,
    image: "https://images.unsplash.com/photo-1548883354-7622d03aca27?w=600&auto=format&fit=crop&q=80",
    description: "Lightweight synthetic insulation jacket made from recycled materials for cold weather protection."
  },
  {
    id: "prod_4",
    name: "Sony WH-1000XM5 Wireless Headphones",
    category: "Electronics",
    price: 398.00,
    stock: 12,
    colors: ["Black", "Silver"],
    aisle: "Aisle 1 - Tech Kiosk",
    section: "Display Case 4",
    in_stock: true,
    sku: "SNY-WH-XM5",
    rating: 4.9,
    image: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80",
    description: "Industry-leading noise canceling with two processors and 8 microphones for unparalleled call quality."
  },
  {
    id: "prod_5",
    name: "Hydro Flask 32 oz Wide Mouth",
    category: "Accessories",
    price: 44.95,
    stock: 32,
    colors: ["Pacific", "Obsidian", "Pacific Blue"],
    aisle: "Aisle 7 - Active Gear",
    section: "Shelf A4",
    in_stock: true,
    sku: "HF-32-WM",
    rating: 4.9,
    image: "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=600&auto=format&fit=crop&q=80",
    description: "TempShield double-wall vacuum insulation keeps drinks cold up to 24 hours."
  },
  {
    id: "prod_6",
    name: "Patagonia Better Sweater Fleece",
    category: "Apparel",
    price: 149.00,
    stock: 4,
    sizes: ["S", "M", "L"],
    aisle: "Aisle 5 - Outerwear",
    section: "Rack 8",
    in_stock: true,
    sku: "PAT-BSF-01",
    rating: 4.7,
    image: "https://images.unsplash.com/photo-1578587018452-892bacefd3f2?w=600&auto=format&fit=crop&q=80",
    description: "Warm, low-bulk fleece jacket dyed with a low-impact process that significantly reduces energy use."
  }
];

// Persistent Inventory Manager
export function getInventoryProducts() {
  const saved = localStorage.getItem('retailmate_inventory_products');
  if (saved) {
    try {
      return JSON.parse(saved);
    } catch (e) {
      console.warn("Failed to parse saved inventory", e);
    }
  }
  return INITIAL_PRODUCTS;
}

export function saveInventoryProducts(products) {
  localStorage.setItem('retailmate_inventory_products', JSON.stringify(products));
}

export function addInventoryItem(newItem) {
  const current = getInventoryProducts();
  const itemToAdd = {
    id: newItem.id || `prod_${Date.now()}`,
    name: newItem.name || "New Retail Item",
    category: newItem.category || "General",
    price: Number(newItem.price) || 29.99,
    stock: Number(newItem.stock) || 10,
    sizes: newItem.sizes ? newItem.sizes.split(',').map(s => s.trim()) : ["M", "L"],
    aisle: newItem.aisle || "Aisle 2 - General",
    section: newItem.section || "Shelf A1",
    in_stock: (Number(newItem.stock) || 10) > 0,
    sku: newItem.sku || `SKU-${Math.floor(1000 + Math.random() * 9000)}`,
    rating: 4.5,
    image: newItem.image || "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=80",
    description: newItem.description || "In-store retail item."
  };
  const updated = [itemToAdd, ...current];
  saveInventoryProducts(updated);
  return updated;
}

export function deleteInventoryItem(id) {
  const current = getInventoryProducts();
  const updated = current.filter(p => p.id !== id);
  saveInventoryProducts(updated);
  return updated;
}

export function updateStockCount(id, delta) {
  const current = getInventoryProducts();
  const updated = current.map(p => {
    if (p.id === id) {
      const newStock = Math.max(0, p.stock + delta);
      return { ...p, stock: newStock, in_stock: newStock > 0 };
    }
    return p;
  });
  saveInventoryProducts(updated);
  return updated;
}

export const MOCK_PRODUCTS = getInventoryProducts();

// Dynamic Sample Orders & Flexible Order ID Lookup
export const MOCK_ORDERS = {
  "ORD001": {
    order_id: "ORD001",
    user_id: "demo-user",
    date: "2026-08-28",
    status: "Delivered",
    eligible_for_return: true,
    days_left: 21,
    items: [
      {
        product_id: "prod_1",
        name: "Nike Air Zoom Pegasus 40",
        size: "9",
        color: "Black/White",
        quantity: 1,
        price: 129.99,
        image: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=80",
        sku: "NK-AZP-40-BL"
      }
    ],
    total: 129.99
  },
  "ORD002": {
    order_id: "ORD002",
    user_id: "demo-user",
    date: "2026-08-15",
    status: "Delivered",
    eligible_for_return: true,
    days_left: 8,
    items: [
      {
        product_id: "prod_4",
        name: "Sony WH-1000XM5 Wireless Headphones",
        size: "N/A",
        color: "Silver",
        quantity: 1,
        price: 398.00,
        image: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80",
        sku: "SNY-WH-XM5"
      }
    ],
    total: 398.00
  },
  "ORD003": {
    order_id: "ORD003",
    user_id: "demo-user",
    date: "2026-06-10",
    status: "Delivered",
    eligible_for_return: false,
    days_left: 0,
    reason_ineligible: "Return window expired (30-day policy exceeded).",
    items: [
      {
        product_id: "prod_3",
        name: "North Face ThermoBall Eco Jacket",
        size: "L",
        color: "Navy",
        quantity: 1,
        price: 198.00,
        image: "https://images.unsplash.com/photo-1548883354-7622d03aca27?w=600&auto=format&fit=crop&q=80",
        sku: "TNF-TB-ECO"
      }
    ],
    total: 198.00
  }
};

/**
 * Flexible Order Lookup Helper:
 * If an Order ID exists, returns it. If custom Order ID is provided, dynamically creates a valid Order object!
 */
export function lookupOrMockOrder(orderIdInput) {
  const cleanId = (orderIdInput || 'ORD001').trim().toUpperCase();
  if (MOCK_ORDERS[cleanId]) {
    return MOCK_ORDERS[cleanId];
  }

  const products = getInventoryProducts();
  const randomProduct = products[Math.floor(Math.random() * products.length)] || INITIAL_PRODUCTS[0];

  return {
    order_id: cleanId,
    user_id: "demo-user",
    date: new Date().toISOString().split('T')[0],
    status: "Delivered",
    eligible_for_return: true,
    days_left: 25,
    items: [
      {
        product_id: randomProduct.id,
        name: randomProduct.name,
        size: randomProduct.sizes ? randomProduct.sizes[0] : "Standard",
        color: "Default",
        quantity: 1,
        price: randomProduct.price,
        image: randomProduct.image,
        sku: randomProduct.sku
      }
    ],
    total: randomProduct.price
  };
}

// Smart Local RAG Query Engine with OpenRouter AI Integration
export async function queryMockRagEngine(queryText, language = 'en', conversationHistory = []) {
  const q = queryText.toLowerCase();
  const currentProducts = getInventoryProducts();

  // Search matching products
  let matchedProducts = currentProducts.filter(p => {
    const pName = p.name.toLowerCase();
    const pCat = p.category.toLowerCase();
    const pAisle = p.aisle.toLowerCase();
    const pDesc = p.description.toLowerCase();
    const pSku = p.sku.toLowerCase();

    return q.split(" ").some(word => word.length > 2 && (
      pName.includes(word) || 
      pCat.includes(word) || 
      pAisle.includes(word) ||
      pDesc.includes(word) ||
      pSku.includes(word)
    ));
  });

  if (matchedProducts.length === 0) {
    if (q.includes("shoe") || q.includes("nike") || q.includes("size")) {
      matchedProducts = currentProducts.filter(p => p.category === "Footwear");
    } else if (q.includes("headphone") || q.includes("sony") || q.includes("tech")) {
      matchedProducts = currentProducts.filter(p => p.category === "Electronics");
    } else if (q.includes("jacket") || q.includes("fleece") || q.includes("apparel")) {
      matchedProducts = currentProducts.filter(p => p.category === "Apparel");
    } else {
      matchedProducts = currentProducts.slice(0, 2);
    }
  }

  // Attempt OpenRouter AI Completion for continuity and intelligent answers
  const openRouterAnswer = await generateOpenRouterCompletion({
    prompt: queryText,
    conversationHistory: conversationHistory,
    language: language,
    inventoryContext: matchedProducts.map(p => ({
      name: p.name,
      category: p.category,
      price: p.price,
      stock: p.stock,
      aisle: p.aisle,
      section: p.section,
      sizes: p.sizes,
      in_stock: p.in_stock
    }))
  });

  if (openRouterAnswer) {
    return {
      answer: openRouterAnswer,
      products: matchedProducts,
      sources: ["RetailMate RAG AI Engine (OpenRouter Gemini)"],
      aisle: matchedProducts[0]?.aisle
    };
  }

  // Fallback responses if offline
  if (q.includes("return") || q.includes("refund") || q.includes("exchange") || q.includes("policy")) {
    return {
      answer: language === 'hi'
        ? "हमारी इन-स्टोर वापसी नीति खरीद की तारीख से 30 दिनों के भीतर रसीद के साथ वापसी या विनिमय की अनुमति देती है।"
        : language === 'kn'
        ? "ನಮ್ಮ ರಿಟರ್ನ್ ಪಾಲಿಸಿಯು 30 ದಿನಗಳ ಒಳಗೆ ರಸೀದಿಯೊಂದಿಗೆ ಉಡುಪುಗಳು ಮತ್ತು ವಸ್ತುಗಳನ್ನು ಹಿಂತಿರುಗಿಸಲು ಅನುಮತಿಸುತ್ತದೆ."
        : "Our in-store return policy allows returns & exchanges within 30 days of purchase with receipt/Order ID. Items must be unworn with tags attached.",
      products: [],
      sources: ["Store Policy Doc - Section 4: Returns & Exchanges"],
      suggested_actions: ["Go to Returns Desk", "Look up Order ORD001"]
    };
  }

  const first = matchedProducts[0] || currentProducts[0];
  const stockMsg = first.stock > 0 
    ? (language === 'hi'
        ? `हाँ! हमारे पास ${first.aisle} (${first.section}) में ${first.name} की ${first.stock} इकाइयाँ उपलब्ध हैं।`
        : language === 'kn'
        ? `ಹೌದು! ನಮ್ಮಲ್ಲಿ ${first.aisle} ನಲ್ಲಿ ${first.name} ನ ${first.stock} ವಸ್ತುಗಳು ಲಭ್ಯವಿವೆ.`
        : `Yes! We currently have ${first.stock} units of ${first.name} in stock at **${first.aisle}**, ${first.section}.`)
    : `Sorry, ${first.name} is currently out of stock in-store. We can arrange home delivery.`;

  return {
    answer: stockMsg,
    products: matchedProducts,
    sources: ["Real-time Inventory RAG Database"],
    aisle: first.aisle
  };
}
