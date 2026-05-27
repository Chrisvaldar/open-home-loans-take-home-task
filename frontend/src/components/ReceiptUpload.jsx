import { useRef, useState } from 'react';
import { scanReceipt } from '../lib/api.js';
import { fileToBase64, getFileMimeType } from '../lib/format.js';
import uploadIcon from '../../frontend_design_references/icons/upload/upload-m.svg';

const MAX_FILE_SIZE_BYTES = 4 * 1024 * 1024;
const ALLOWED_MIME_TYPES = new Set([
  'image/jpeg',
  'image/jpg',
  'image/png',
  'image/heic',
  'image/heif',
  'image/webp',
]);
const ACCEPTED_IMAGE_TYPES =
  'image/jpeg,image/jpg,image/png,image/heic,image/webp,.jpg,.jpeg,.png,.heic,.webp';

/**
 * @param {File} file
 * @returns {boolean}
 */
function isAllowedImageType(file) {
  const mimeType = getFileMimeType(file);
  return ALLOWED_MIME_TYPES.has(mimeType);
}

/**
 * @param {{ onSuccess: (items: string[]) => void, onError?: (message: string) => void }} props
 */
export default function ReceiptUpload({ onSuccess, onError }) {
  const inputRef = useRef(null);
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState(null);
  const [warning, setWarning] = useState(null);

  const handleFile = async (file) => {
    setError(null);
    setWarning(null);

    if (!file) {
      return;
    }

    if (!isAllowedImageType(file)) {
      const message =
        'Please upload a JPEG, PNG, HEIC, or WebP image (up to 4 MB).';
      setError(message);
      onError?.(message);
      return;
    }

    if (file.size > MAX_FILE_SIZE_BYTES) {
      const message = 'Image is too large. Please use an image under 4 MB.';
      setError(message);
      onError?.(message);
      return;
    }

    setScanning(true);

    try {
      const { base64, mimeType } = await fileToBase64(file);
      const data = await scanReceipt(base64, mimeType);

      if (!data.items?.length) {
        setWarning('No items found on receipt. Try a clearer photo.');
        return;
      }

      onSuccess(data.items);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Receipt scan failed.';
      setError(message);
      onError?.(message);
    } finally {
      setScanning(false);
      if (inputRef.current) {
        inputRef.current.value = '';
      }
    }
  };

  const handleInputChange = (event) => {
    const file = event.target.files?.[0];
    void handleFile(file);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files?.[0];
    void handleFile(file);
  };

  return (
    <div className="space-y-4">
      <div
        className="rounded-lg border border-dashed border-border-default bg-surface-primary p-8 text-center"
        onDragOver={(event) => event.preventDefault()}
        onDrop={handleDrop}
      >
        <img
          src={uploadIcon}
          alt=""
          aria-hidden="true"
          className="mx-auto mb-4 h-6 w-5 invert"
        />
        <p className="text-base leading-6 text-text-primary">
          Upload a receipt photo
        </p>
        <p className="mt-1 text-sm text-text-secondary">
          JPEG, PNG, HEIC, or WebP up to 4 MB. We&apos;ll extract items into
          your list.
        </p>

        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED_IMAGE_TYPES}
          className="sr-only"
          disabled={scanning}
          onChange={handleInputChange}
        />

        <button
          type="button"
          disabled={scanning}
          onClick={() => inputRef.current?.click()}
          className="mt-6 rounded-md border border-border-default bg-white px-6 py-3 text-sm font-medium text-black transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {scanning ? 'Scanning receipt…' : 'Choose image file'}
        </button>

        {scanning && (
          <div className="mt-4 flex items-center justify-center gap-3 text-sm text-text-secondary">
            <div
              className="spinner h-4 w-4 rounded-full border-2 border-border-default border-t-accent"
              aria-hidden="true"
            />
            Extracting items from your receipt
          </div>
        )}
      </div>

      {error && (
        <div
          role="alert"
          className="rounded-lg border border-destructive bg-white p-4 text-sm text-black"
        >
          {error}
        </div>
      )}

      {warning && (
        <div
          role="status"
          className="rounded-lg border border-accent bg-surface-secondary p-4 text-sm text-text-primary"
        >
          {warning}
        </div>
      )}
    </div>
  );
}
