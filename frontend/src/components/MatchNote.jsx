import { formatCurrency } from '../lib/format.js';

/**
 * @param {string | null | undefined} note
 * @param {import('../lib/types.js').Confidence | string | null | undefined} confidence
 * @param {number} [saving]
 */
export default function MatchNote({ note, confidence, saving = 0 }) {
  if (!note && !confidence && !(saving > 0)) {
    return null;
  }

  const parts = [];

  if (saving > 0) {
    parts.push(`Saves ${formatCurrency(saving)}`);
  }

  if (note) {
    parts.push(note);
  }

  if (confidence) {
    parts.push(`${confidence} confidence`);
  }

  return (
    <p className="font-numeric mt-1 text-xs leading-4 text-text-secondary">
      {parts.join(' · ')}
    </p>
  );
}
