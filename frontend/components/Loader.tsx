export default function Loader({ label = "Loading..." }: { label?: string }) {
  return (
    <div className="flex items-center gap-2 text-sm text-[var(--muted)]">
      <span className="size-2 animate-ping rounded-full bg-white/60" />
      <span>{label}</span>
    </div>
  );
}
