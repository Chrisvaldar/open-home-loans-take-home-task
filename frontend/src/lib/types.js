/**
 * @typedef {"branded" | "generic" | "no_match"} MatchType
 */

/**
 * @typedef {"woolworths" | "coles" | "tie" | "no_comparison"} ItemWinner
 */

/**
 * @typedef {"woolworths" | "coles" | "tie"} BasketWinner
 */

/**
 * @typedef {"high" | "medium" | "low"} Confidence
 */

/**
 * @typedef {Object} StoreProduct
 * @property {string} name
 * @property {string} brand
 * @property {number} price
 * @property {string} size
 * @property {number | null} unit_price
 * @property {string | null} unit
 * @property {boolean} on_special
 * @property {Confidence} confidence
 */

/**
 * @typedef {Object} BreakdownItem
 * @property {string} item
 * @property {MatchType} match_type
 * @property {StoreProduct | null} woolworths
 * @property {StoreProduct | null} coles
 * @property {ItemWinner} winner
 * @property {number} saving
 * @property {string | null} note
 */

/**
 * @typedef {Object} CompareResponse
 * @property {BasketWinner} winner
 * @property {number} total_woolworths
 * @property {number} total_coles
 * @property {number} savings
 * @property {number} annualised_savings
 * @property {BreakdownItem[]} breakdown
 */

/**
 * @typedef {Object} ReceiptResponse
 * @property {string[]} items
 */

export {};
