import { getApiBaseUrl, isMockModeForced } from '../config/apiConfig';
import { queryMockRagEngine, MOCK_ORDERS } from './mockData';

/**
 * Sends prompt query to FastAPI backend /api/assistant/query
 * Payload: { query: string, user_id: string }
 * Checks primary URL and alternative RAG port (8001) before using fallback engine.
 */
export async function queryAssistant(query, userId = "demo-user") {
  const baseUrl = getApiBaseUrl();
  const forceMock = isMockModeForced();

  if (forceMock) {
    console.log("[RetailMate API] Running in Forced Mock Mode");
    await new Promise(res => setTimeout(res, 500));
    const mockRes = queryMockRagEngine(query);
    return {
      isMock: true,
      data: mockRes
    };
  }

  // Attempt standard configured URL, then fallback to RAG port 8001
  const urlsToTry = [
    baseUrl,
    baseUrl.includes('8000') ? baseUrl.replace('8000', '8001') : 'http://localhost:8001'
  ];

  for (const targetUrl of urlsToTry) {
    try {
      const response = await fetch(`${targetUrl}/api/assistant/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          user_id: userId,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        return {
          isMock: false,
          data: data
        };
      }
    } catch (err) {
      // Continue to next URL candidate
    }
  }

  // If live backend servers are offline, return smooth local RAG fallback
  console.log(`[RetailMate API] Live FastAPI server unavailable. Using smart local RAG engine.`);
  await new Promise(res => setTimeout(res, 600));
  const fallbackRes = queryMockRagEngine(query);
  return {
    isMock: true,
    isFallback: true,
    data: fallbackRes
  };
}

/**
 * Sends return initiation request to FastAPI backend /api/returns/initiate
 * Payload: { order_id: string, action: string }
 */
export async function initiateReturn(orderId, action = "return") {
  const baseUrl = getApiBaseUrl();
  const forceMock = isMockModeForced();

  if (forceMock) {
    console.log("[RetailMate API] Processing return in Forced Mock Mode");
    await new Promise(res => setTimeout(res, 600));
    return processMockReturn(orderId, action);
  }

  // Attempt standard configured URL, then fallback to Backend port 8002
  const urlsToTry = [
    baseUrl,
    baseUrl.includes('8000') ? baseUrl.replace('8000', '8002') : 'http://localhost:8002'
  ];

  for (const targetUrl of urlsToTry) {
    try {
      const response = await fetch(`${targetUrl}/api/returns/initiate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          order_id: orderId,
          action: action,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        return {
          isMock: false,
          data: data
        };
      }
    } catch (err) {
      // Continue to next URL candidate
    }
  }

  // Fallback to local mock return handler
  console.log(`[RetailMate API] Live FastAPI return service unavailable. Processing via local engine.`);
  await new Promise(res => setTimeout(res, 600));
  return processMockReturn(orderId, action);
}

// Local mock return helper
function processMockReturn(orderId, action) {
  const order = MOCK_ORDERS[orderId];

  if (!order) {
    return {
      isMock: true,
      data: {
        success: false,
        message: `Order ID '${orderId}' was not found in the retail database. Please verify your receipt.`,
        ticket_id: null
      }
    };
  }

  if (!order.eligible_for_return) {
    return {
      isMock: true,
      data: {
        success: false,
        eligible: false,
        message: order.reason_ineligible || "This order is no longer eligible for return/exchange.",
        ticket_id: null
      }
    };
  }

  const ticketId = `RM-TCK-${Math.floor(100000 + Math.random() * 900000)}`;
  const item = order.items[0];

  return {
    isMock: true,
    data: {
      success: true,
      eligible: true,
      ticket_id: ticketId,
      action: action,
      order_id: orderId,
      status: "APPROVED_READY_FOR_COUNTER",
      message: action === "exchange"
        ? `Exchange authorization #${ticketId} created! Bring your item to Aisle 3 counter to swap sizes.`
        : `Return ticket #${ticketId} generated! Instant refund will be credited to original payment method upon barcode drop-off.`,
      product_name: item.name,
      amount: order.total,
      created_at: new Date().toISOString()
    }
  };
}
