import woolworthsLogo from '../assets/brands/woolworths.svg';
import colesLogo from '../assets/brands/coles.svg';

/**
 * @param {{ winner: import('../lib/types.js').BasketWinner | import('../lib/types.js').ItemWinner, size?: 'sm' | 'md' }} props
 */
export default function StoreBadge({ winner, size = 'md' }) {
  const sizeClasses = size === 'sm' ? 'h-6 w-6' : 'h-10 w-10';

  if (winner === 'woolworths') {
    return (
      <img
        src={woolworthsLogo}
        alt="Woolworths"
        className={`${sizeClasses} shrink-0 rounded-full`}
      />
    );
  }

  if (winner === 'coles') {
    return (
      <img
        src={colesLogo}
        alt="Coles"
        className={`${sizeClasses} shrink-0 rounded-full`}
      />
    );
  }

  return (
    <span
      className={`inline-flex ${sizeClasses} items-center justify-center rounded-full border border-border-default text-xs font-medium text-text-secondary`}
    >
      —
    </span>
  );
}
