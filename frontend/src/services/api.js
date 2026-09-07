import { getApiBaseUrl, isMockModeForced } from '../config/apiConfig';
import { normalizeLanguage } from './i18n';
import { queryMockRagEngine, MOCK_ORDERS } from './mockData';

/**
 * Sends a query to the RetailMate Agent / RAG Service.
 *
 * Agent Service: http://127.0.0.1:8003
 * RAG Service: http://127.0.0.1:8001
 * Backend: http://127.0.0.1:8002
 */
export async function queryAssistant(
  query,
  userId = 'demo-user',
  language = 'en'
) {
  const baseUrl = getApiBaseUrl();
  const selectedLanguage = normalizeLanguage ? normalizeLanguage(language) : language;
  const forceMock = isMockModeForced();

  if (forceMock) {
    console.log('[RetailMate API] Running in Forced Mock Mode');
    await new Promise((resolve) => setTimeout(resolve, 500));
    const mockRes = await queryMockRagEngine(query, selectedLanguage);
    return {
      isMock: true,
      data: mockRes,
    };
  }

  // URLs to attempt (configured base URL, port 8003 for Agent, port 8001 for RAG)
  const urlsToTry = [
    baseUrl,
    baseUrl.includes('8000') ? baseUrl.replace('8000', '8003') : 'http://localhost:8003',
    baseUrl.includes('8000') ? baseUrl.replace('8000', '8001') : 'http://localhost:8001'
  ];

  for (const targetUrl of urlsToTry) {
    try {
      const requestStartedAt = new Date().toISOString();
      const requestStartedMs = performance.now();

      const response = await fetch(`${targetUrl}/api/assistant/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          user_id: userId,
          language: selectedLanguage,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const responseCompletedAt = new Date().toISOString();
        const responseCompletedMs = performance.now();

        data.timing = {
          ...(data.timing || {}),
          frontend_agent_request_start: requestStartedAt,
          frontend_agent_response_end: responseCompletedAt,
          frontend_agent_latency_ms: responseCompletedMs - requestStartedMs,
        };

        return {
          isMock: false,
          data: data,
        };
      }
    } catch (error) {
      // Continue trying next target port
    }
  }

  // Fallback to local RAG engine if live servers are unreachable
  console.log('[RetailMate API] Live FastAPI server unavailable. Using smart local RAG engine.');
  await new Promise((res) => setTimeout(res, 600));
  const fallbackRes = await queryMockRagEngine(query, selectedLanguage);
  return {
    isMock: true,
    isFallback: true,
    data: fallbackRes,
  };
}

/**
 * Sends a return request to POST /api/returns/initiate
 */
export async function initiateReturn(orderId, action = 'return') {
  const baseUrl = getApiBaseUrl();
  const forceMock = isMockModeForced();

  if (forceMock) {
    console.log('[RetailMate API] Processing return in Forced Mock Mode');
    await new Promise((resolve) => setTimeout(resolve, 600));
    return processMockReturn(orderId, action);
  }

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
          data: data,
        };
      }
    } catch (error) {
      // Try next port
    }
  }

  console.log('[RetailMate API] Live return backend unavailable. Processing via client engine.');
  await new Promise((res) => setTimeout(res, 600));
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
        ticket_id: null,
      },
    };
  }

  if (!order.eligible_for_return) {
    return {
      isMock: true,
      data: {
        success: false,
        eligible: false,
        message: order.reason_ineligible || 'This order is no longer eligible for return/exchange.',
        ticket_id: null,
      },
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
      status: 'APPROVED_READY_FOR_COUNTER',
      message:
        action === 'exchange'
          ? `Exchange authorization #${ticketId} created! Bring your item to Aisle 3 counter to swap sizes.`
          : `Return ticket #${ticketId} generated! Instant refund will be credited to original payment method upon barcode drop-off.`,
      product_name: item.name,
      amount: order.total,
      created_at: new Date().toISOString(),
    },
  };
}