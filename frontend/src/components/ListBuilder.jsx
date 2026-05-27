import { useState } from 'react';
import ReceiptUpload from './ReceiptUpload.jsx';

/**
 * @param {{
 *   items: string[],
 *   setItems: React.Dispatch<React.SetStateAction<string[]>>,
 *   onCompare: () => void,
 *   onReceiptCompareStart?: () => void,
 *   onReceiptCompareSuccess: (results: import('../lib/types.js').CompareResponse) => void,
 *   onReceiptError?: (message: string) => void,
 * }} props
 */
export default function ListBuilder({
  items,
  setItems,
  onCompare,
  onReceiptCompareStart,
  onReceiptCompareSuccess,
  onReceiptError,
}) {
  const [inputValue, setInputValue] = useState('');
  const [activeTab, setActiveTab] = useState('manual');

  const addItem = () => {
    const trimmed = inputValue.trim();
    if (!trimmed) {
      return;
    }

    setItems((current) => {
      const exists = current.some(
        (item) => item.toLowerCase() === trimmed.toLowerCase(),
      );
      if (exists) {
        return current;
      }
      return [...current, trimmed];
    });
    setInputValue('');
  };

  const removeItem = (index) => {
    setItems((current) => current.filter((_, itemIndex) => itemIndex !== index));
  };

  const clearList = () => {
    setItems([]);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    addItem();
  };

  const handleReceiptCompareSuccess = (results) => {
    onReceiptCompareSuccess(results);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          onClick={() => setActiveTab('manual')}
          className={`rounded-full px-4 py-1.5 text-sm font-medium transition-colors ${
            activeTab === 'manual'
              ? 'bg-white text-black'
              : 'text-text-secondary hover:text-text-primary'
          }`}
        >
          Build list
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('receipt')}
          className={`rounded-full px-4 py-1.5 text-sm font-medium transition-colors ${
            activeTab === 'receipt'
              ? 'bg-white text-black'
              : 'text-text-secondary hover:text-text-primary'
          }`}
        >
          Scan receipt
        </button>
      </div>

      {activeTab === 'manual' ? (
        <div className="space-y-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label
                htmlFor="item-input"
                className="mb-1 block text-sm font-medium text-text-secondary"
              >
                Add an item
              </label>
              <div className="flex flex-col gap-3 sm:flex-row">
                <input
                  id="item-input"
                  type="text"
                  value={inputValue}
                  onChange={(event) => setInputValue(event.target.value)}
                  placeholder="e.g. milk, a2 milk 2L, bread"
                  className="min-w-0 flex-1 rounded-sm border border-border-default bg-surface-secondary px-4 py-3 text-base text-text-primary outline-none placeholder:text-text-secondary focus:border-accent"
                />
                <button
                  type="submit"
                  className="rounded-md bg-white px-6 py-3 text-sm font-medium text-black transition-opacity hover:opacity-90"
                >
                  Add
                </button>
              </div>
            </div>
          </form>

          <div className="rounded-lg border border-border-default bg-surface-secondary p-4">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-sm font-medium text-text-secondary">
                Your list
              </h2>
              <span className="font-numeric text-xs text-text-secondary">
                {items.length} item{items.length === 1 ? '' : 's'}
              </span>
            </div>

            {items.length === 0 ? (
              <p className="py-6 text-center text-sm text-text-secondary">
                Add items you buy each week, then compare stores.
              </p>
            ) : (
              <ul className="divide-y divide-border-default">
                {items.map((item, index) => (
                  <li
                    key={`${item}-${index}`}
                    className="flex items-center justify-between gap-4 py-3"
                  >
                    <span className="text-base text-text-primary">{item}</span>
                    <button
                      type="button"
                      onClick={() => removeItem(index)}
                      className="rounded-md border border-border-default px-3 py-1 text-sm text-text-secondary transition-colors hover:border-text-primary hover:text-text-primary"
                      aria-label={`Remove ${item}`}
                    >
                      Remove
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <button
              type="button"
              onClick={onCompare}
              disabled={items.length === 0}
              className="w-full rounded-md bg-accent px-6 py-3 text-sm font-medium text-black transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40 sm:w-auto"
            >
              Compare
            </button>
            {items.length > 0 && (
              <button
                type="button"
                onClick={clearList}
                className="w-full rounded-md border border-destructive bg-transparent px-6 py-3 text-sm font-medium text-destructive transition-colors hover:bg-destructive/10 sm:w-auto"
              >
                Clear list
              </button>
            )}
          </div>
        </div>
      ) : (
        <ReceiptUpload
          onCompareStart={onReceiptCompareStart}
          onCompareSuccess={handleReceiptCompareSuccess}
          onError={onReceiptError}
        />
      )}
    </div>
  );
}
