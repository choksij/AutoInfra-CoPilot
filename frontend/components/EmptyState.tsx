export default function EmptyState({
  title = "No data yet",
  subtitle = "Kick off a run to see results here.",
  action,
}: {
  title?: string;
  subtitle?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-[var(--panel)] p-8 text-center">
      <div className="mx-auto mb-4 size-10 rounded-xl bg-white/10" />
      <h3 className="text-base font-semibold">{title}</h3>
      <p className="mt-1 text-sm text-[var(--muted)]">{subtitle}</p>
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
