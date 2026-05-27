import MatchNote from './MatchNote.jsx';
import StoreBadge from './StoreBadge.jsx';
import {
  formatCurrency,
  formatUnitPrice,
  formatWinnerLabel,
} from '../lib/format.js';

/** @typedef {import('../lib/types.js').CompareResponse} CompareResponse */
/** @typedef {import('../lib/types.js').BreakdownItem} BreakdownItem */
/** @typedef {import('../lib/types.js').StoreProduct} StoreProduct */
/** @typedef {import('../lib/types.js').BasketWinner} BasketWinner */

/**
 * @param {BasketWinner} winner
 */
function heroAccentClass(winner) {
  switch (winner) {
    case 'woolworths':
      return 'border-success';
    case 'coles':
      return 'border-destructive';
    default:
      return 'border-accent';
  }
}

/**
 * @param {BasketWinner} winner
 */
function heroHeadline(winner) {
  switch (winner) {
    case 'woolworths':
      return 'Shop at Woolworths this week';
    case 'coles':
      return 'Shop at Coles this week';
    default:
      return "It's a tie this week";
  }
}

/**
 * @param {{ product: StoreProduct | null }} props
 */
function StoreProductCell({ product }) {
  if (!product) {
    return <span className="text-sm text-text-secondary">Not found</span>;
  }

  const unitPrice = formatUnitPrice(product);

  return (
    <div className="space-y-1">
      <p className="text-sm font-medium text-text-primary">{product.name}</p>
      <p className="text-xs text-text-secondary">{product.brand}</p>
      <p className="text-sm text-text-primary">
        <span className="font-numeric">{formatCurrency(product.price)}</span>
        {product.size ? (
          <span className="font-numeric text-text-secondary">
            {' '}
            · {product.size}
          </span>
        ) : null}
      </p>
      {unitPrice && (
        <p className="font-numeric text-xs text-text-secondary">{unitPrice}</p>
      )}
      {product.on_special && (
        <span className="inline-block rounded-full border border-accent px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide text-accent">
          On special
        </span>
      )}
    </div>
  );
}

/**
 * @param {BreakdownItem} row
 */
function rowConfidence(row) {
  return row.woolworths?.confidence ?? row.coles?.confidence ?? 'medium';
}

/**
 * @param {{ row: BreakdownItem }} props
 */
function BreakdownCard({ row }) {
  return (
    <article className="rounded-lg border border-border-default bg-surface-secondary p-4">
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-wide text-text-secondary">
            Search term
          </p>
          <h3 className="mt-1 text-base font-medium text-text-primary">
            {row.item}
          </h3>
        </div>
        <div className="flex items-center gap-2">
          {row.winner === 'woolworths' || row.winner === 'coles' ? (
            <StoreBadge winner={row.winner} size="sm" />
          ) : (
            <span className="text-xs text-text-secondary">
              {formatWinnerLabel(row.winner)}
            </span>
          )}
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <p className="mb-2 text-xs font-medium uppercase tracking-wide text-text-secondary">
            Woolworths
          </p>
          <StoreProductCell product={row.woolworths} />
        </div>
        <div>
          <p className="mb-2 text-xs font-medium uppercase tracking-wide text-text-secondary">
            Coles
          </p>
          <StoreProductCell product={row.coles} />
        </div>
      </div>

      <MatchNote note={row.note} confidence={rowConfidence(row)} />
    </article>
  );
}

/**
 * @param {{
 *   results: CompareResponse,
 *   onCompareAgain: () => void,
 * }} props
 */
export default function Results({ results, onCompareAgain }) {
  return (
    <div className="space-y-8">
      <section
        className={`rounded-lg border border-border-default border-t-4 bg-surface-secondary p-6 md:p-8 ${heroAccentClass(results.winner)}`}
      >
        <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
          <div className="flex items-start gap-4">
            {(results.winner === 'woolworths' ||
              results.winner === 'coles') && (
              <StoreBadge winner={results.winner} />
            )}
            <div>
              <p className="text-sm font-medium text-text-secondary">
                Overall winner
              </p>
              <h2 className="mt-1 text-4xl leading-none text-text-primary md:text-[56px]">
                {heroHeadline(results.winner)}
              </h2>
              <p className="mt-4 text-lg text-text-secondary">
                You&apos;ll save{' '}
                <span className="font-numeric font-medium text-text-primary">
                  {formatCurrency(results.savings)}
                </span>{' '}
                on your list
              </p>
              <p className="mt-2 text-sm text-text-secondary">
                That&apos;s{' '}
                <span className="font-numeric text-text-primary">
                  {formatCurrency(results.annualised_savings)}/year
                </span>{' '}
                if you keep switching
              </p>
            </div>
          </div>

          <div className="rounded-md border border-border-default bg-surface-primary px-4 py-3 text-sm">
            <div className="flex justify-between gap-6">
              <span className="text-text-secondary">Woolworths total</span>
              <span className="font-numeric font-medium text-text-primary">
                {formatCurrency(results.total_woolworths)}
              </span>
            </div>
            <div className="mt-2 flex justify-between gap-6">
              <span className="text-text-secondary">Coles total</span>
              <span className="font-numeric font-medium text-text-primary">
                {formatCurrency(results.total_coles)}
              </span>
            </div>
          </div>
        </div>
      </section>

      <section className="space-y-4">
        <div>
          <h2 className="text-[32px] leading-10 text-text-primary">
            Item breakdown
          </h2>
          <p className="mt-1 text-sm text-text-secondary">
            Prices and matches for each item on your list
          </p>
        </div>

        <div className="hidden overflow-x-auto rounded-lg border border-border-default md:block">
          <table className="min-w-full divide-y divide-border-default">
            <thead className="bg-surface-secondary">
              <tr>
                {['Item', 'Woolworths', 'Coles', 'Winner', 'Note'].map(
                  (heading) => (
                    <th
                      key={heading}
                      scope="col"
                      className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-text-secondary"
                    >
                      {heading}
                    </th>
                  ),
                )}
              </tr>
            </thead>
            <tbody className="divide-y divide-border-default bg-surface-primary">
              {results.breakdown.map((row) => (
                <tr key={row.item}>
                  <td className="px-4 py-4 align-top text-sm font-medium text-text-primary">
                    {row.item}
                  </td>
                  <td className="px-4 py-4 align-top">
                    <StoreProductCell product={row.woolworths} />
                  </td>
                  <td className="px-4 py-4 align-top">
                    <StoreProductCell product={row.coles} />
                  </td>
                  <td className="px-4 py-4 align-top">
                    {row.winner === 'woolworths' || row.winner === 'coles' ? (
                      <div className="flex items-center gap-2">
                        <StoreBadge winner={row.winner} size="sm" />
                        <span className="text-sm text-text-primary">
                          {formatWinnerLabel(row.winner)}
                        </span>
                      </div>
                    ) : (
                      <span className="text-sm text-text-secondary">
                        {formatWinnerLabel(row.winner)}
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-4 align-top">
                    <MatchNote
                      note={row.note}
                      confidence={rowConfidence(row)}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="space-y-4 md:hidden">
          {results.breakdown.map((row) => (
            <BreakdownCard key={row.item} row={row} />
          ))}
        </div>
      </section>

      <button
        type="button"
        onClick={onCompareAgain}
        className="w-full rounded-md bg-white px-6 py-3 text-sm font-medium text-black transition-opacity hover:opacity-90 sm:w-auto"
      >
        Compare again
      </button>
    </div>
  );
}
