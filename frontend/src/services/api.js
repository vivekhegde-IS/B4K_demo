import { getApiBaseUrl, isMockModeForced } from '../config/apiConfig';
import { normalizeLanguage } from './i18n';
import { queryMockRagEngine, MOCK_ORDERS } from './mockData';

/**
 * Sends a query to the RetailMate Agent Service.
 *
 * Agent Service:
 * http://127.0.0.1:8003
 *
 * Agent Service then communicates with:
 * RAG Service:
 * http://127.0.0.1:8001
 *
 * Backend:
 * http://127.0.0.1:8002
 */
export async function queryAssistant(
  query,
  userId = 'demo-user',
  language = 'en'
) {
  const baseUrl = getApiBaseUrl();
  const selectedLanguage = normalizeLanguage(language);

  const forceMock = isMockModeForced();

  /*
   * ---------------------------------------------------------
   * OPTIONAL FORCED MOCK MODE
   * ---------------------------------------------------------
   *
   * This is kept so the existing frontend can still be
   * deliberately switched into mock mode if required.
   *
   * Normally this should be false.
   */
  if (forceMock) {
    console.log(
      '[RetailMate API] Running in Forced Mock Mode'
    );

    await new Promise((resolve) =>
      setTimeout(resolve, 600)
    );

    const mockRes = queryMockRagEngine(query);

    return {
      isMock: true,
      data: mockRes,
    };
  }

  /*
   * ---------------------------------------------------------
   * REAL AGENT SERVICE
   * ---------------------------------------------------------
   */

  try {
    const requestStartedAt = new Date().toISOString();
    const requestStartedMs = performance.now();

    console.log(
      `[RetailMate API] Sending query to ${baseUrl}`
    );

    console.log(
      `[RetailMate API] Language: ${selectedLanguage}`
    );

    const response = await fetch(
      `${baseUrl}/api/assistant/query`,
      {
        method: 'POST',

        headers: {
          'Content-Type': 'application/json',
        },

        body: JSON.stringify({
          query: query,
          user_id: userId,
          language: selectedLanguage,
        }),
      }
    );

    /*
     * If the server returns an error, DO NOT silently switch
     * to mock mode.
     */
    if (!response.ok) {
      const errorText = await response.text();

      throw new Error(
        `Agent Service returned HTTP ${response.status}: ${errorText}`
      );
    }

    const data = await response.json();
    const responseCompletedAt = new Date().toISOString();
    const responseCompletedMs = performance.now();

    data.timing = {
      ...(data.timing || {}),
      frontend_agent_request_start: requestStartedAt,
      frontend_agent_response_end: responseCompletedAt,
      frontend_agent_latency_ms:
        responseCompletedMs - requestStartedMs,
    };

    console.info('[Voice Pipeline] RAG', data.timing);

    console.log(
      '[RetailMate API] Real Agent response:',
      data
    );

    return {
      isMock: false,
      data: data,
    };
  } catch (error) {
    /*
     * IMPORTANT:
     *
     * Previously this function silently called
     * queryMockRagEngine() here.
     *
     * That made debugging very difficult because the UI
     * appeared to work while actually using fake data.
     *
     * We now throw the error so ChatPage can display the
     * actual connection problem.
     */
    console.error(
      '[RetailMate API] Agent Service request failed:',
      error
    );

    throw error;
  }
}


/**
 * ---------------------------------------------------------
 * RETURN INITIATION
 * ---------------------------------------------------------
 *
 * Sends a return request to:
 *
 * POST /api/returns/initiate
 *
 * The mock return functionality is retained because the
 * frontend currently supports the mock workflow as well.
 */
export async function initiateReturn(
  orderId,
  action = 'return'
) {
  const baseUrl = getApiBaseUrl();

  const forceMock = isMockModeForced();

  /*
   * Forced mock mode
   */
  if (forceMock) {
    console.log(
      '[RetailMate API] Processing return in Forced Mock Mode'
    );

    await new Promise((resolve) =>
      setTimeout(resolve, 800)
    );

    return processMockReturn(orderId, action);
  }

  /*
   * Real backend
   */
  try {
    console.log(
      `[RetailMate API] Sending return request to ${baseUrl}`
    );

    const response = await fetch(
      `${baseUrl}/api/returns/initiate`,
      {
        method: 'POST',

        headers: {
          'Content-Type': 'application/json',
        },

        body: JSON.stringify({
          order_id: orderId,
          action: action,
        }),
      }
    );

    if (!response.ok) {
      const errorText = await response.text();

      throw new Error(
        `Return API returned HTTP ${response.status}: ${errorText}`
      );
    }

    const data = await response.json();

    return {
      isMock: false,
      data: data,
    };
  } catch (error) {
    console.error(
      '[RetailMate API] Return request failed:',
      error
    );

    /*
     * Keep existing mock return fallback for now.
     *
     * We are only removing the silent mock fallback from
     * the assistant query because that was hiding the
     * Agent/RAG connection problem.
     */
    return processMockReturn(orderId, action);
  }
}


/**
 * ---------------------------------------------------------
 * LOCAL MOCK RETURN HELPER
 * ---------------------------------------------------------
 */
function processMockReturn(
  orderId,
  action
) {
  const order = MOCK_ORDERS[orderId];

  /*
   * Order doesn't exist
   */
  if (!order) {
    return {
      isMock: true,

      data: {
        success: false,
        message:
          `Order ID '${orderId}' was not found in the retail database. Please verify your receipt.`,
        ticket_id: null,
      },
    };
  }

  /*
   * Order is not eligible
   */
  if (!order.eligible_for_return) {
    return {
      isMock: true,

      data: {
        success: false,
        eligible: false,
        message:
          order.reason_ineligible ||
          'This order is no longer eligible for return/exchange.',
        ticket_id: null,
      },
    };
  }

  /*
   * Generate mock ticket
   */
  const ticketId =
    `RM-TCK-${Math.floor(
      100000 + Math.random() * 900000
    )}`;

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
          : `Return ticket #${ticketId} generated! Instant refund of $${order.total.toFixed(
              2
            )} will be credited to original payment method upon barcode drop-off.`,

      product_name: item.name,
      amount: order.total,
      created_at: new Date().toISOString(),
    },
  };
}