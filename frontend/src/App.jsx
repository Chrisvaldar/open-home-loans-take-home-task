import { useState } from 'react';
import { compareBasket } from './lib/api.js';
import ListBuilder from './components/ListBuilder.jsx';
import LoadingScreen from './components/LoadingScreen.jsx';
import Results from './components/Results.jsx';
import homeShieldIcon from '../frontend_design_references/icons/home-shield/home-shield-s.svg';
import warningIcon from '../frontend_design_references/icons/warning-triangle.svg';

export default function App() {
  const [view, setView] = useState('list');
  const [results, setResults] = useState(null);
  const [items, setItems] = useState([]);
  const [compareSource, setCompareSource] = useState('manual');
  const [error, setError] = useState(null);

  const handleCompare = async () => {
    if (items.length === 0) {
      setError('Add at least one item to your list before comparing.');
      setView('error');
      return;
    }

    setError(null);
    setView('loading');

    try {
      const data = await compareBasket(items, compareSource);
      setResults(data);
      setView('results');
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Comparison failed. Please try again.',
      );
      setView('error');
    }
  };

  const handleReceiptItemsExtracted = (extractedItems) => {
    setItems(extractedItems);
    setCompareSource('receipt');
    setError(null);
  };

  const handleClearList = () => {
    setItems([]);
    setCompareSource('manual');
  };

  const handleReceiptError = (message) => {
    setError(message);
    setView('list');
  };

  const handleCompareAgain = () => {
    setView('list');
  };

  const handleDismissError = () => {
    setError(null);
    setView('list');
  };

  return (
    <main className="min-h-screen bg-surface-primary px-4 py-8 text-text-primary">
      <div className="mx-auto max-w-3xl">
        <header className="mb-8 flex items-center gap-3">
          <img
            src={homeShieldIcon}
            alt="Frugl"
            className="h-5 w-[18px]"
          />
          <h1 className="text-[40px] leading-none text-text-primary">Frugl</h1>
        </header>

        {view === 'list' && (
          <ListBuilder
            items={items}
            setItems={setItems}
            onCompare={handleCompare}
            onReceiptItemsExtracted={handleReceiptItemsExtracted}
            onClearList={handleClearList}
            onReceiptError={handleReceiptError}
          />
        )}

        {view === 'loading' && <LoadingScreen />}

        {view === 'results' && results && (
          <Results results={results} onCompareAgain={handleCompareAgain} />
        )}

        {view === 'error' && (
          <section className="space-y-6">
            <div
              role="alert"
              className="rounded-lg border border-destructive bg-white p-6 text-black"
            >
              <div className="flex items-start gap-4">
                <span className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-destructive">
                  <img
                    src={warningIcon}
                    alt=""
                    aria-hidden="true"
                    className="h-4 w-4"
                  />
                </span>
                <div>
                  <h2 className="text-base font-medium">Something went wrong</h2>
                  <p className="mt-2 text-sm text-black/80">
                    {error ?? 'An unexpected error occurred.'}
                  </p>
                </div>
              </div>
            </div>

            <button
              type="button"
              onClick={handleDismissError}
              className="rounded-md bg-accent px-6 py-3 text-sm font-medium text-black transition-opacity hover:opacity-90"
            >
              Try again
            </button>
          </section>
        )}
      </div>
    </main>
  );
}
