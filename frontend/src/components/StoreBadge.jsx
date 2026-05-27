import woolworthsLogo from '../assets/brands/woolworths.svg';
import colesLogo from '../assets/brands/coles.svg';

/**
 * @param {{ winner: import('../lib/types.js').BasketWinner | import('../lib/types.js').ItemWinner, size?: 'sm' | 'md' }} props
 */
export default function StoreBadge({ winner, size = 'md' }) {
  if (winner === 'woolworths') {
    return (
      <img
        src={woolworthsLogo}
        alt="Woolworths"
        className={`${size === 'sm' ? 'h-6 w-6' : 'h-10 w-10'} shrink-0 object-contain`}
      />
    );
  }

  if (winner === 'coles') {
    return (
      <img
        src={colesLogo}
        alt="Coles"
        className={`${size === 'sm' ? 'h-4' : 'h-6'} shrink-0 object-contain`}
      />
    );
  }

  const sizeClasses = size === 'sm' ? 'h-6 w-6' : 'h-10 w-10';

  return (
    <span
      className={`inline-flex ${sizeClasses} items-center justify-center rounded-full border border-border-default text-xs font-medium text-text-secondary`}
    >
      —
    </span>
  );
}
