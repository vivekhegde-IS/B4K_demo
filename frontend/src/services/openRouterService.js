// OpenRouter AI Service Client
const getApiKey = () => {
  return (
    import.meta.env?.VITE_OPENROUTER_API_KEY ||
    localStorage.getItem('retailmate_openrouter_key') ||
    ''
  );
};

const OPENROUTER_URL = 'https://openrouter.ai/api/v1/chat/completions';
const MODEL = 'google/gemini-2.0-flash-lite-001'; // Fast, free/low-cost model on OpenRouter

/**
 * Generates intelligent, context-aware AI response using OpenRouter LLM.
 */
export async function generateOpenRouterCompletion({ prompt, conversationHistory = [], language = 'en', inventoryContext = [] }) {
  const apiKey = getApiKey();
  if (!apiKey) {
    return null;
  }

  const systemInstructions = `You are RetailMate, a friendly and highly knowledgeable in-store retail kiosk assistant.
Language preference: ${language === 'hi' ? 'Hindi (हिंदी)' : language === 'kn' ? 'Kannada (ಕನ್ನಡ)' : 'English'}.
Always reply in the user's chosen language (${language === 'hi' ? 'Hindi' : language === 'kn' ? 'Kannada' : 'English'}) clearly and concisely.

Current Store Inventory Context:
${JSON.stringify(inventoryContext, null, 2)}

Store Return Policy:
- 30-day return window with receipt/Order ID for unworn items with tags.
- Exchanges allowed for different sizes or colors at Aisle 3 counter.
- Electronics require original box.

Instructions:
1. Provide helpful, accurate responses.
2. If asked about stock, specify exact aisle location and available stock count.
3. Keep response concise (2-4 sentences) suitable for a touchscreen retail kiosk display.
4. Always respond in ${language === 'hi' ? 'Hindi script (हिंदी)' : language === 'kn' ? 'Kannada script (ಕನ್ನಡ)' : 'English'}.`;

  const messages = [
    { role: 'system', content: systemInstructions },
    ...conversationHistory.slice(-4).map(msg => ({
      role: msg.sender === 'user' ? 'user' : 'assistant',
      content: msg.text
    })),
    { role: 'user', content: prompt }
  ];

  try {
    const response = await fetch(OPENROUTER_URL, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'HTTP-Referer': 'https://retailmate-kiosk.local',
        'X-Title': 'RetailMate Kiosk',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: MODEL,
        messages: messages,
        temperature: 0.7,
        max_tokens: 350,
      }),
    });

    if (!response.ok) {
      console.warn(`[OpenRouter API] Status ${response.status}: ${await response.text()}`);
      return null;
    }

    const data = await response.json();
    const aiMessage = data.choices?.[0]?.message?.content;
    return aiMessage ? aiMessage.trim() : null;
  } catch (error) {
    console.warn(`[OpenRouter API Error] ${error.message}`);
    return null;
  }
}
