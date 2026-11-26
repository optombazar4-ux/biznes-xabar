import { SITE_NAME } from "./site";

/**
 * Collapses whitespace and trims text cleanly on a word boundary so it fits
 * within `maxLen` characters.
 */
export function truncateWords(text, maxLen) {
  const clean = String(text || "").replace(/\s+/g, " ").trim();
  if (!clean || clean.length <= maxLen) return clean;
  const slice = clean.slice(0, Math.max(1, maxLen - 1));
  const lastSpace = slice.lastIndexOf(" ");
  const cut = lastSpace >= Math.floor(maxLen * 0.55) ? slice.slice(0, lastSpace) : slice;
  return `${cut.replace(/[,:;.\-–—\s]+$/, "")}…`;
}

/**
 * Formats a page title for Next.js metadata so the final rendered `<title>`
 * stays within `maxLen` characters (default 65) even with the layout template.
 */
export function fitMetaTitle(raw, siteName = SITE_NAME, maxLen = 65) {
  const clean = String(raw || "").replace(/\s+/g, " ").trim();
  if (!clean) return siteName;

  if (clean.toLowerCase().includes(siteName.toLowerCase())) {
    return { absolute: truncateWords(clean, maxLen) };
  }

  const suffix = ` — ${siteName}`;
  if (clean.length + suffix.length <= maxLen) {
    return clean;
  }

  return { absolute: truncateWords(clean, maxLen) };
}

/**
 * Extracts a plain string title from `fitMetaTitle()` output for Open Graph / Twitter.
 */
export function plainMetaTitle(titleValue) {
  return typeof titleValue === "string" ? titleValue : titleValue?.absolute || SITE_NAME;
}

/**
 * Trims meta descriptions to Google/Yandex snippet limits (default 155 chars).
 */
export function fitMetaDescription(raw, maxLen = 155) {
  return truncateWords(raw, maxLen);
}
