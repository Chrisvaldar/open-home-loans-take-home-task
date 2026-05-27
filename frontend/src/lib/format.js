/** @typedef {import('./types.js').StoreProduct} StoreProduct */
/** @typedef {import('./types.js').ItemWinner} ItemWinner */
/** @typedef {import('./types.js').BasketWinner} BasketWinner */

const currencyFormatter = new Intl.NumberFormat('en-AU', {
  style: 'currency',
  currency: 'AUD',
});

/**
 * @param {number} amount
 * @returns {string}
 */
export function formatCurrency(amount) {
  return currencyFormatter.format(amount);
}

/**
 * @param {StoreProduct | null | undefined} product
 * @returns {string | null}
 */
export function formatUnitPrice(product) {
  if (!product || product.unit_price == null || !product.unit) {
    return null;
  }

  return `${formatCurrency(product.unit_price)} ${product.unit}`;
}

/**
 * @param {ItemWinner | BasketWinner} winner
 * @returns {string}
 */
export function formatWinnerLabel(winner) {
  switch (winner) {
    case 'woolworths':
      return 'Woolworths';
    case 'coles':
      return 'Coles';
    case 'tie':
      return 'Tie';
    case 'no_comparison':
      return 'No comparison';
    default:
      return winner;
  }
}

/**
 * @param {File} file
 * @returns {Promise<string>}
 */
export function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();

    reader.onload = () => {
      const result = reader.result;
      if (typeof result !== 'string') {
        reject(new Error('Could not read file.'));
        return;
      }

      const base64 = result.replace(/^data:image\/jpeg;base64,/, '');
      resolve(base64);
    };

    reader.onerror = () => {
      reject(new Error('Could not read file.'));
    };

    reader.readAsDataURL(file);
  });
}
