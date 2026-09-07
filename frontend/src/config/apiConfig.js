// API Configuration Manager & Currency Settings
const STORAGE_KEY = 'retailmate_api_base_url';
const MOCK_MODE_KEY = 'retailmate_force_mock_mode';
const CURRENCY_KEY = 'retailmate_currency';
export const DEFAULT_API_BASE_URL = 'http://127.0.0.1:8003';
export const USD_TO_INR_RATE = 85.50; // Standard exchange rate 1 USD = 85.50 INR

export function getApiBaseUrl() {
  const saved = localStorage.getItem(STORAGE_KEY);
  return saved || import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL;
}

export function setApiBaseUrl(url) {
  let cleanUrl = url.trim();
  if (cleanUrl.endsWith('/')) {
    cleanUrl = cleanUrl.slice(0, -1);
  }
  localStorage.setItem(STORAGE_KEY, cleanUrl);
  return cleanUrl;
}

export function isMockModeForced() {
  return localStorage.getItem(MOCK_MODE_KEY) === 'true';
}

export function setForceMockMode(force) {
  localStorage.setItem(MOCK_MODE_KEY, force ? 'true' : 'false');
}

export function getCurrency() {
  return localStorage.getItem(CURRENCY_KEY) || 'INR'; // Default to INR
}

export function setCurrency(curr) {
  localStorage.setItem(CURRENCY_KEY, curr);
}

export function formatPrice(amountInUSD, targetCurrency = getCurrency()) {
  if (targetCurrency === 'INR') {
    const amountInINR = Math.round(amountInUSD * USD_TO_INR_RATE);
    return `₹${amountInINR.toLocaleString('en-IN')}`;
  }
  return `$${amountInUSD.toFixed(2)}`;
}

export function resetApiConfig() {
  localStorage.removeItem(STORAGE_KEY);
  localStorage.removeItem(MOCK_MODE_KEY);
  localStorage.removeItem(CURRENCY_KEY);
}
