export async function compareBasket(items) {
  const response = await fetch('/api/compare', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ items }),
  });

  if (!response.ok) {
    throw new Error(`Compare failed: ${response.status}`);
  }

  return response.json();
}

export async function scanReceipt(base64Image) {
  const response = await fetch('/api/receipt', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image: base64Image }),
  });

  if (!response.ok) {
    throw new Error(`Receipt scan failed: ${response.status}`);
  }

  return response.json();
}
