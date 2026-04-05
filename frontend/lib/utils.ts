export function cn(..._parts: (string | undefined | false)[]): string {
  return _parts.filter(Boolean).join(" ");
}
