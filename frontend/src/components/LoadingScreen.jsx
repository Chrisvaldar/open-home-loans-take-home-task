export default function LoadingScreen() {
  return (
    <section
      className="flex min-h-[320px] flex-col items-center justify-center rounded-lg border border-border-default bg-surface-secondary p-8 text-center"
      aria-live="polite"
      aria-busy="true"
    >
      <div
        className="spinner mb-6 h-10 w-10 rounded-full border-2 border-border-default border-t-accent"
        role="status"
        aria-label="Loading"
      />
      <p className="text-lg leading-7 text-text-primary">
        Finding the best prices this week…
      </p>
      <p className="mt-2 text-sm text-text-secondary">
        Comparing Woolworths and Coles for your list
      </p>
      <div className="mt-8 h-1 w-full max-w-xs overflow-hidden rounded-full bg-border-default">
        <div className="h-full w-1/3 animate-pulse rounded-full bg-accent" />
      </div>
    </section>
  );
}
