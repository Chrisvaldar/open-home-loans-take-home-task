/**
 * @param {string | null | undefined} note
 * @param {import('../lib/types.js').Confidence | string | null | undefined} confidence
 */
export default function MatchNote({ note, confidence }) {
  if (!note && !confidence) {
    return null;
  }

  const parts = [];

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
