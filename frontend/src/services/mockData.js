// Mock Store Inventory Dataset & RAG Responder
export const MOCK_PRODUCTS = [
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

// Smart Local RAG Query Mock Engine
export function queryMockRagEngine(queryText) {
  const q = queryText.toLowerCase();
  
  // Return policy check
  if (q.includes("return") || q.includes("refund") || q.includes("exchange") || q.includes("policy")) {
    return {
      answer: "Our in-store return policy allows returns & exchanges within 30 days of purchase with original receipt/Order ID. Items must be unworn with tags attached. Electronics require original box and packaging.",
      products: [],
      sources: ["Store Policy Doc - Section 4: Returns & Exchanges"],
      suggested_actions: ["Go to Returns Desk", "Look up Order ORD001"]
    };
  }

  // Aisle location query
  if (q.includes("where") || q.includes("find") || q.includes("aisle") || q.includes("location")) {
    let matchedProducts = MOCK_PRODUCTS.filter(p => 
      q.includes(p.name.toLowerCase()) || 
      q.includes(p.category.toLowerCase()) || 
      (q.includes("shoe") && p.category === "Footwear") ||
      (q.includes("nike") && p.name.includes("Nike")) ||
      (q.includes("headphone") && p.name.includes("Sony")) ||
      (q.includes("jacket") && p.category === "Apparel") ||
      (q.includes("water bottle") && p.category === "Accessories")
    );

    if (matchedProducts.length === 0) matchedProducts = [MOCK_PRODUCTS[0], MOCK_PRODUCTS[1]];

    return {
      answer: `You can find ${matchedProducts[0].name} in **${matchedProducts[0].aisle}** (${matchedProducts[0].section}). Follow the cyan ceiling signage towards section ${matchedProducts[0].category}.`,
      products: matchedProducts,
      sources: ["In-Store Map Database - Section Aisle Index"],
      aisle: matchedProducts[0].aisle
    };
  }

  // Stock / product availability query
  let matchedProducts = MOCK_PRODUCTS.filter(p => {
    const pName = p.name.toLowerCase();
    const pCat = p.category.toLowerCase();
    return q.split(" ").some(word => word.length > 3 && (pName.includes(word) || pCat.includes(word)));
  });

  if (matchedProducts.length === 0) {
    if (q.includes("shoe") || q.includes("nike") || q.includes("size 9")) {
      matchedProducts = [MOCK_PRODUCTS[0]];
    } else if (q.includes("headphone") || q.includes("sony")) {
      matchedProducts = [MOCK_PRODUCTS[3]];
    } else {
      matchedProducts = MOCK_PRODUCTS.slice(0, 2);
    }
  }

  const first = matchedProducts[0];
  const stockMsg = first.stock > 0 
    ? `Yes! We currently have ${first.stock} units of ${first.name} in stock at **${first.aisle}**, ${first.section}.`
    : `Sorry, ${first.name} is currently out of stock in-store. We can arrange free delivery to your home.`;

  return {
    answer: stockMsg,
    products: matchedProducts,
    sources: ["Real-time Inventory RAG Database"],
    aisle: first.aisle
  };
}
