// Regional Language Translation Dictionary (English, Hindi, Kannada)
const LANGUAGE_KEY = 'retailmate_language';

export const LANGUAGES = [
  { code: 'en', name: 'English', native: 'English', speechLang: 'en-IN', flag: '🇮🇳' },
  { code: 'hi', name: 'Hindi', native: 'हिंदी', speechLang: 'hi-IN', flag: '🇮🇳' },
  { code: 'kn', name: 'Kannada', native: 'ಕನ್ನಡ', speechLang: 'kn-IN', flag: '🇮🇳' }
];

export const LANGUAGE_CODES = Object.freeze(
  LANGUAGES.reduce((codes, language) => {
    codes[language.code] = language.speechLang;
    return codes;
  }, {})
);

export function normalizeLanguage(code = 'en') {
  return LANGUAGES.some((language) => language.code === code)
    ? code
    : 'en';
}

export function getSpeechLanguage(code = 'en') {
  return LANGUAGE_CODES[normalizeLanguage(code)];
}

export function getStoredLanguage() {
  return localStorage.getItem(LANGUAGE_KEY) || 'en';
}

export function setStoredLanguage(code) {
  localStorage.setItem(LANGUAGE_KEY, code);
}

export const TRANSLATIONS = {
  en: {
    // Header & Nav
    brandName: "RetailMate",
    kioskTitle: "Kiosk AI",
    storeLocation: "Downtown Flagship Store #402",
    navAssistant: "Assistant",
    navProducts: "Products",
    navReturns: "Returns & Exchange",
    navTimeline: "Timeline",
    navManageInventory: "Manage Stock",
    demoMode: "Demo Mode",
    fastapiReady: "FastAPI Ready",
    resetKiosk: "Reset Session",

    // Home Page
    welcomeTitle: "Welcome to",
    welcomeSubtitle: "Ask about product availability in size & color, find store aisle locations, check return policies, or start an instant return.",
    browseInventoryBtn: "Browse Full Inventory",
    returnsCounterBtn: "Returns & Exchange Counter",
    inputPlaceholder: "Ask anything (e.g., 'Do you have Nike shoes in size 9?')",
    listeningState: "Listening to your query...",
    speakingState: "Speaking response...",
    queryingRagState: "Querying RAG Inventory...",
    tapMicInstruction: "Tap microphone or type below to ask",
    suggestedTitle: "Suggested Kiosk Questions",

    // Suggested Chips
    suggested1: "Do you have Nike shoes in size 9?",
    suggested1Cat: "Stock Check",
    suggested2: "Where can I find Nike shoes in store?",
    suggested2Cat: "Aisle Navigation",
    suggested3: "Can I return my product without a receipt?",
    suggested3Cat: "Return Policy",
    suggested4: "Initiate return for Order ORD001",
    suggested4Cat: "Returns Desk",

    // Inventory Page
    inventoryTitle: "Product Catalog & Aisle Locations",
    inventorySubtitle: "Real-time stock availability, department sections, and aisle navigation.",
    searchPlaceholder: "Search products or aisles...",
    allCategories: "All",
    allAvailability: "All Availability",
    inStockOnly: "In Stock Only",
    lowStockOnly: "Low Stock (≤ 5 units)",

    // Product Card & Stock
    inStock: "In Stock",
    lowStock: "Low Stock",
    outOfStock: "Out of Stock",
    unitsAvailable: "available",
    unitsLeft: "left",
    viewMap: "View Map",
    askAssistantAboutItem: "Ask Assistant About Item",
    categoryFootwear: "Footwear",
    categoryApparel: "Apparel",
    categoryElectronics: "Electronics",
    categoryAccessories: "Accessories",

    // Returns Page
    returnsTitle: "Returns & Product Exchanges",
    returnsSubtitle: "Enter your Order ID or select sample receipt to initiate instant refund authorization.",
    orderInputLabel: "Enter Order Identification (Order ID)",
    lookupOrderBtn: "Lookup Order",
    quickReceipts: "Quick Receipts:",
    eligibleBadge: "Eligible for Return / Exchange",
    ineligibleBadge: "Ineligible for Return",
    orderItemsHeader: "Order Items",
    actionChoiceTitle: "Choose Action Type",
    fullRefundReturn: "Full Refund Return",
    fullRefundDesc: "Refund total to original payment method",
    sizeExchange: "Size / Item Exchange",
    sizeExchangeDesc: "Swap size or color directly at customer counter",
    initiateTicketBtn: "Initiate Return Ticket",
    
    // Ticket Modal
    verifiedTicket: "Verified Return Ticket",
    exchangeCreated: "Exchange Ticket Created!",
    returnApproved: "Return Ticket Approved!",
    ticketRef: "Ticket Reference",
    scanAtCounter: "Scan at Customer Counter Aisle 1",
    refundValue: "Refund Value:",
    printTicket: "Print Ticket",
    doneBtn: "Done",

    // Chat Page
    chatTitle: "RetailMate Assistant",
    chatSubtitle: "Interactive Voice & Text Conversation History",
    clearHistory: "Clear History",
    noHistoryTitle: "No Chat History Yet",
    noHistoryDesc: "Start asking about shoes, sizes, store aisle maps, or return policy to see live AI responses.",
    typePlaceholder: "Type your question...",
    retryBtn: "Retry",

    // Aisle Map
    floorNavTitle: "In-Store Floor Navigator",
    locating: "Locating",
    youAreHere: "You Are Here (Kiosk #402)",
    targetAisle: "Target Aisle",
    gotIt: "Got it, thanks!"
  },

  hi: {
    // Header & Nav
    brandName: "रिटेलमेट",
    kioskTitle: "कियोस्क एआई",
    storeLocation: "फ्लैगशिप स्टोर #402",
    navAssistant: "सहायक",
    navProducts: "उत्पाद सूची",
    navReturns: "वापसी और विनिमय",
    navTimeline: "बातचीत",
    demoMode: "डेमो मोड",
    fastapiReady: "फास्टएपीआई तैयार",
    resetKiosk: "सत्र रीसेट करें",

    // Home Page
    welcomeTitle: "आपका स्वागत है",
    welcomeSubtitle: "साइज और रंग में उत्पाद की उपलब्धता पूछें, दुकान में ऐसल ढूंढें, वापसी नीति जांचें या तुरंत वापसी शुरू करें।",
    browseInventoryBtn: "पूरी इन्वेंटरी देखें",
    returnsCounterBtn: "वापसी एवं विनिमय काउंटर",
    inputPlaceholder: "कुछ भी पूछें (उदा. 'क्या साइज 9 में नाइके के जूते उपलब्ध हैं?')",
    listeningState: "आपकी बात सुनी जा रही है...",
    speakingState: "उत्तर बोला जा रहा है...",
    queryingRagState: "इन्वेंटरी खोजी जा रही है...",
    tapMicInstruction: "माइक्रोफ़ोन दबाएं या नीचे टाइप करें",
    suggestedTitle: "सुझाए गए प्रश्न",

    // Suggested Chips
    suggested1: "क्या साइज 9 में नाइके के जूते उपलब्ध हैं?",
    suggested1Cat: "स्टॉक जांच",
    suggested2: "दुकान में नाइके के जूते कहाँ मिलेंगे?",
    suggested2Cat: "ऐसल लोकेशन",
    suggested3: "क्या बिना रसीद के उत्पाद वापस किया जा सकता है?",
    suggested3Cat: "वापसी नीति",
    suggested4: "ऑर्डर ORD001 के लिए वापसी शुरू करें",
    suggested4Cat: "वापसी डेस्क",

    // Inventory Page
    inventoryTitle: "उत्पाद कैटलॉग और ऐसल स्थान",
    inventorySubtitle: "वास्तविक समय स्टॉक उपलब्धता, विभाग अनुभाग और ऐसल नेविगेशन।",
    searchPlaceholder: "उत्पाद या ऐसल खोजें...",
    allCategories: "सभी",
    allAvailability: "सभी उपलब्धता",
    inStockOnly: "केवल स्टॉक में उपलब्ध",
    lowStockOnly: "कम स्टॉक (≤ 5 इकाइयाँ)",

    // Product Card & Stock
    inStock: "स्टॉक में उपलब्ध",
    lowStock: "कम स्टॉक",
    outOfStock: "आउट ऑफ स्टॉक",
    unitsAvailable: "उपलब्ध",
    unitsLeft: "शेष",
    viewMap: "मैप देखें",
    askAssistantAboutItem: "सहायक से उत्पाद के बारे में पूछें",
    categoryFootwear: "फुटवियर",
    categoryApparel: "कपड़े",
    categoryElectronics: "इलेक्ट्रॉनिक्स",
    categoryAccessories: "सामान",

    // Returns Page
    returnsTitle: "उत्पाद वापसी एवं विनिमय",
    returnsSubtitle: "तुरंत धनवापसी टिकट के लिए अपनी ऑर्डर आईडी दर्ज करें या सैंपल रसीद चुनें।",
    orderInputLabel: "ऑर्डर आईडी दर्ज करें (Order ID)",
    lookupOrderBtn: "ऑर्डर खोजें",
    quickReceipts: "त्वरित रसीदें:",
    eligibleBadge: "वापसी / विनिमय के लिए योग्य",
    ineligibleBadge: "वापसी के लिए अयोग्य",
    orderItemsHeader: "ऑर्डर किए गए सामान",
    actionChoiceTitle: "कार्रवाई का प्रकार चुनें",
    fullRefundReturn: "पूर्ण धनवापसी (Full Refund)",
    fullRefundDesc: "मूल भुगतान विधि में राशि वापस करें",
    sizeExchange: "साइज / वस्तु विनिमय (Exchange)",
    sizeExchangeDesc: "काउंटर पर सीधे साइज या रंग बदलें",
    initiateTicketBtn: "वापसी टिकट जारी करें",

    // Ticket Modal
    verifiedTicket: "सत्यापित वापसी टिकट",
    exchangeCreated: "विनिमय टिकट तैयार!",
    returnApproved: "वापसी टिकट स्वीकृत!",
    ticketRef: "टिकट संख्या",
    scanAtCounter: "कस्टमर काउंटर ऐसल 1 पर स्कैन करें",
    refundValue: "धनवापसी मूल्य:",
    printTicket: "टिकट प्रिंट करें",
    doneBtn: "हो गया",

    // Chat Page
    chatTitle: "रिटेलमेट एआई सहायक",
    chatSubtitle: "इंटरैक्टिव आवाज एवं पाठ इतिहास",
    clearHistory: "इतिहास मिटाएं",
    noHistoryTitle: "कोई इतिहास नहीं है",
    noHistoryDesc: "जूते, साइज, दुकान के नक्शे या वापसी नीति के बारे में प्रश्न पूछना शुरू करें।",
    typePlaceholder: "अपना प्रश्न टाइप करें...",
    retryBtn: "पुनः प्रयास करें",

    // Aisle Map
    floorNavTitle: "इन-स्टोर नेविगेटर",
    locating: "खोज रहे हैं",
    youAreHere: "आप यहाँ हैं (कियोस्क #402)",
    targetAisle: "लक्षित ऐसल",
    gotIt: "समझ गया, धन्यवाद!"
  },

  kn: {
    // Header & Nav
    brandName: "ರೀಟೇಲ್‌ಮೇಟ್",
    kioskTitle: "ಕಿಯೋಸ್ಕ್ AI",
    storeLocation: "ಫ್ಲ್ಯಾಗ್‌ಶಿಪ್ ಸ್ಟೋರ್ #402",
    navAssistant: "ಸಹಾಯಕ",
    navProducts: "ಉತ್ಪನ್ನಗಳು",
    navReturns: "ರಿಟರ್ನ್ಸ್ & ವಿನಿಮಯ",
    navTimeline: "ಸಂಭಾಷಣೆ",
    demoMode: "ಡೆಮೊ ಮೋಡ್",
    fastapiReady: "FastAPI ಸಿದ್ಧವಾಗಿದೆ",
    resetKiosk: "ಸೆಷನ್ ಮರುಹೊಂದಿಸಿ",

    // Home Page
    welcomeTitle: "ಸ್ವಾಗತ",
    welcomeSubtitle: "ಉತ್ಪನ್ನದ ಲಭ್ಯತೆ, ಸೈಜ್, ಅಂಗಡಿಯ ಸಾಲು (Aisle) ಸ್ಥಳ, ರಿಟರ್ನ್ ಪಾಲಿಸಿ ಅಥವಾ ತಕ್ಷಣದ ರಿಟರ್ನ್‌ಗಾಗಿ ಕೇಳಿ.",
    browseInventoryBtn: "ಸಂಪೂರ್ಣ ದಾಸ್ತಾನು ನೋಡಿ",
    returnsCounterBtn: "ರಿಟರ್ನ್ಸ್ ಮತ್ತು ವಿನಿಮಯ ಕೌಂಟರ್",
    inputPlaceholder: "ಏನನ್ನಾದರೂ ಕೇಳಿ (ಉದಾ. 'ಸೈಜ್ 9 ರಲ್ಲಿ ನೈಕ್ ಶೂಗಳು ಲಭ್ಯವಿದೆಯೇ?')",
    listeningState: "ನಿಮ್ಮ ಧ್ವನಿಯನ್ನು ಆಲಿಸಲಾಗುತ್ತಿದೆ...",
    speakingState: "ಉತ್ತರವನ್ನು ಹೇಳಲಾಗುತ್ತಿದೆ...",
    queryingRagState: "ದಾಸ್ತಾನು ಹುಡುಕಲಾಗುತ್ತಿದೆ...",
    tapMicInstruction: "ಮೈಕ್ರೋಫೋನ್ ಸ್ಪರ್ಶಿಸಿ ಅಥವಾ ಕೆಳಗೆ ಟೈಪ್ ಮಾಡಿ",
    suggestedTitle: "ಸೂಚಿಸಿದ ಪ್ರಶ್ನೆಗಳು",

    // Suggested Chips
    suggested1: "ಸೈಜ್ 9 ರಲ್ಲಿ ನೈಕ್ ಶೂಗಳು ಲಭ್ಯವಿದೆಯೇ?",
    suggested1Cat: "ಸ್ಟಾಕ್ ಪರೀಕ್ಷೆ",
    suggested2: "ಅಂಗಡಿಯಲ್ಲಿ ನೈಕ್ ಶೂಗಳನ್ನು ಎಲ್ಲಿ ಕಾಣಬಹುದು?",
    suggested2Cat: "ಸಾಲು ನಕ್ಷೆ",
    suggested3: "ರಸೀದಿ ಇಲ್ಲದೆ ಉತ್ಪನ್ನವನ್ನು ಹಿಂತಿರುಗಿಸಬಹುದೇ?",
    suggested3Cat: "ರಿಟರ್ನ್ ಪಾಲಿಸಿ",
    suggested4: "ಆರ್ಡರ್ ORD001 ಗಾಗಿ ಹಿಂತಿರುಗಿಸುವಿಕೆಯನ್ನು ಪ್ರಾರಂಭಿಸಿ",
    suggested4Cat: "ರಿಟರ್ನ್ ಡೆಸ್ಕ್",

    // Inventory Page
    inventoryTitle: "ಉತ್ಪನ್ನಗಳ ಪಟ್ಟಿ ಮತ್ತು ಸಾಲಿಕಾ ಸ್ಥಳಗಳು",
    inventorySubtitle: "ನೈಜ-ಸಮಯದ ಸ್ಟಾಕ್ ಲಭ್ಯತೆ, ವಿಭಾಗಗಳು ಮತ್ತು ಸಾಲು ನಕ್ಷೆ.",
    searchPlaceholder: "ಉತ್ಪನ್ನಗಳು ಅಥವಾ ಸಾಲುಗಳನ್ನು ಹುಡುಕಿ...",
    allCategories: "ಎಲ್ಲಾ",
    allAvailability: "ಎಲ್ಲಾ ಲಭ್ಯತೆ",
    inStockOnly: "ಸ್ಟಾಕ್‌ನಲ್ಲಿರುವುದು ಮಾತ್ರ",
    lowStockOnly: "ಕಡಿಮೆ ಸ್ಟಾಕ್ (≤ 5)",

    // Product Card & Stock
    inStock: "ಸ್ಟಾಕ್‌ನಲ್ಲಿದೆ",
    lowStock: "ಕಡಿಮೆ ಸ್ಟಾಕ್",
    outOfStock: "ಸ್ಟಾಕ್‌ನಲ್ಲಿಲ್ಲ",
    unitsAvailable: "ಲಭ್ಯವಿದೆ",
    unitsLeft: "ಉಳಿದಿದೆ",
    viewMap: "ನಕ್ಷೆ ನೋಡಿ",
    askAssistantAboutItem: "ಸಹಾಯಕರ ಬಳಿ ಕೇಳಿ",
    categoryFootwear: "ಪಾದರಕ್ಷೆಗಳು",
    categoryApparel: "ಉಡುಪುಗಳು",
    categoryElectronics: "ಎಲೆಕ್ಟ್ರಾನಿಕ್ಸ್",
    categoryAccessories: "ಪರಿಕರಗಳು",

    // Returns Page
    returnsTitle: "ಉತ್ಪನ್ನ ರಿಟರ್ನ್ಸ್ & ವಿನಿಮಯ",
    returnsSubtitle: "ತ್ವರಿತ ಮರುಪಾವತಿ ಟಿಕೆಟ್‌ಗಾಗಿ ನಿಮ್ಮ ಆರ್ಡರ್ ಐಡಿ ನಮೂದಿಸಿ ಅಥವಾ ಮಾದರಿ ಸ್ವೀಕೃತಿ ಆಯ್ಕೆಮಾಡಿ.",
    orderInputLabel: "ಆರ್ಡರ್ ಐಡಿ ನಮೂದಿಸಿ (Order ID)",
    lookupOrderBtn: "ಆರ್ಡರ್ ಹುಡುಕಿ",
    quickReceipts: "ತ್ವರಿತ ರಸೀದಿಗಳು:",
    eligibleBadge: "ಹಿಂತಿರುಗಿಸಲು / ವಿನಿಮಯಕ್ಕೆ ಅರ್ಹವಾಗಿದೆ",
    ineligibleBadge: "ಹಿಂತಿರುಗಿಸಲು ಅರ್ಹವಲ್ಲ",
    orderItemsHeader: "ಆರ್ಡರ್ ಮಾಡಿದ ವಸ್ತುಗಳು",
    actionChoiceTitle: "ಕ್ರಿಯೆಯ ಪ್ರಕಾರವನ್ನು ಆಯ್ಕೆಮಾಡಿ",
    fullRefundReturn: "ಸಂಪೂರ್ಣ ಮರುಪಾವತಿ (Full Refund)",
    fullRefundDesc: "ಮೂಲ ಪಾವತಿ ವಿಧಾನಕ್ಕೆ ಹಣ ಹಿಂತಿರುಗಿಸಿ",
    sizeExchange: "ಸೈಜ್ / ವಸ್ತು ವಿನಿಮಯ (Exchange)",
    sizeExchangeDesc: "ಕೌಂಟರ್‌ನಲ್ಲಿ ನೇರವಾಗಿ ಸೈಜ್ ಅಥವಾ ಬಣ್ಣ ಬದಲಾಯಿಸಿ",
    initiateTicketBtn: "ರಿಟರ್ನ್ ಟಿಕೆಟ್ ನೀಡಿ",

    // Ticket Modal
    verifiedTicket: "ದೃಢೀಕರಿಸಿದ ರಿಟರ್ನ್ ಟಿಕೆಟ್",
    exchangeCreated: "ವಿನಿಮಯ ಟಿಕೆಟ್ ಸಿದ್ಧವಾಗಿದೆ!",
    returnApproved: "ರಿಟರ್ನ್ ಟಿಕೆಟ್ ಅನುಮೋದಿಸಲಾಗಿದೆ!",
    ticketRef: "ಟಿಕೆಟ್ ಸಂಖ್ಯೆ",
    scanAtCounter: "ಕಸ್ಟಮರ್ ಕೌಂಟರ್‌ನಲ್ಲಿ ಸ್ಕ್ಯಾನ್ ಮಾಡಿ",
    refundValue: "ಮರುಪಾವತಿ ಮೌಲ್ಯ:",
    printTicket: "ಟಿಕೆಟ್ ಪ್ರಿಂಟ್ ಮಾಡಿ",
    doneBtn: "ಪೂರ್ಣಗೊಂಡಿದೆ",

    // Chat Page
    chatTitle: "ರೀಟೇಲ್‌ಮೇಟ್ AI ಸಹಾಯಕ",
    chatSubtitle: "ಧ್ವನಿ ಮತ್ತು ಪಠ್ಯ ಸಂಭಾಷಣೆ ಇತಿಹಾಸ",
    clearHistory: "ಇತಿಹಾಸ ಅಳಿಸಿ",
    noHistoryTitle: "ಯಾವುದೇ ಇತಿಹಾಸವಿಲ್ಲ",
    noHistoryDesc: "ಶೂಗಳು, ಸೈಜ್, ಅಂಗಡಿಯ ನಕ್ಷೆ ಅಥವಾ ರಿಟರ್ನ್ ಪಾಲಿಸಿ ಬಗ್ಗೆ ಪ್ರಶ್ನೆಗಳನ್ನು ಕೇಳಲು ಪ್ರಾರಂಭಿಸಿ.",
    typePlaceholder: "ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಟೈಪ್ ಮಾಡಿ...",
    retryBtn: "ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ",

    // Aisle Map
    floorNavTitle: "ಅಂಗಡಿಯ ಸಾಲು ನಕ್ಷೆ",
    locating: "ಹುಡುಕಲಾಗುತ್ತಿದೆ",
    youAreHere: "ನೀವು ಇಲ್ಲಿದ್ದೀರಿ (ಕಿಯೋಸ್ಕ್ #402)",
    targetAisle: "ಗುರಿ ಸಾಲು",
    gotIt: "ಅರ್ಥವಾಯಿತು, ಧನ್ಯವಾದಗಳು!"
  }
};

export function t(key, lang = getStoredLanguage()) {
  const dictionary = TRANSLATIONS[lang] || TRANSLATIONS.en;
  return dictionary[key] || TRANSLATIONS.en[key] || key;
}
