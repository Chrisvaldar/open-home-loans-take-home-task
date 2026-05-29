import woolworthsLogo from '../assets/brands/woolworths.svg';
import colesLogo from '../assets/brands/coles.svg';

const SIZE_CLASSES = {
  sm: {
    woolworths: 'h-6 w-6',
    coles: 'h-4',
    tie: 'h-6 w-6',
  },
  md: {
    woolworths: 'h-10 w-10',
    coles: 'h-6',
    tie: 'h-10 w-10',
  },
  lg: {
    woolworths: 'h-12 w-12',
    coles: 'h-8',
    tie: 'h-12 w-12',
  },
};

/**
 * @param {{ winner: import('../lib/types.js').BasketWinner | import('../lib/types.js').ItemWinner, size?: 'sm' | 'md' | 'lg' }} props
 */
export default function StoreBadge({ winner, size = 'md' }) {
  const classes = SIZE_CLASSES[size] ?? SIZE_CLASSES.md;

  if (winner === 'woolworths') {
    return (
      <img
        src={woolworthsLogo}
        alt="Woolworths"
        className={`${classes.woolworths} shrink-0 object-contain`}
      />
    );
  }

  if (winner === 'coles') {
    return (
      <img
        src={colesLogo}
        alt="Coles"
        className={`${classes.coles} shrink-0 object-contain`}
      />
    );
  }

  const sizeClasses = classes.tie;

  return (
    <span
      className={`inline-flex ${sizeClasses} items-center justify-center rounded-full border border-border-default text-xs font-medium text-text-secondary`}
    >
      —
    </span>
  );
}
