/**
 * @param {Response} response
 * @returns {Promise<string>}
 */
async function getErrorMessage(response, fallback) {
  try {
    const data = await response.json();
    if (typeof data?.detail === 'string') {
      return data.detail;
    }
    if (Array.isArray(data?.detail)) {
      return data.detail.map((entry) => entry.msg ?? String(entry)).join(', ');
    }
  } catch {
    // Response body is not JSON.
  }

  return fallback;
}

/**
 * @param {string[]} items
 * @returns {Promise<import('./types.js').CompareResponse>}
 */
export async function compareBasket(items) {
  const response = await fetch('/api/compare', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ items }),
  });

  if (!response.ok) {
    const message = await getErrorMessage(
      response,
      `Compare failed: ${response.status}`,
    );
    throw new Error(message);
  }

  return response.json();
}

/**
 * @param {string} base64Image
 * @returns {Promise<import('./types.js').ReceiptResponse>}
 */
export async function scanReceipt(base64Image) {
  const response = await fetch('/api/receipt', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image: base64Image }),
  });

  if (!response.ok) {
    const message = await getErrorMessage(
      response,
      `Receipt scan failed: ${response.status}`,
    );
    throw new Error(message);
  }

  return response.json();
}
