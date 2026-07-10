"use client";

import { useEffect } from "react";
import { markRead } from "../lib/progress";

// Dars sahifasi ochilganda uni "o'qilgan" deb belgilaydi (UI ko'rsatmaydi).
export default function MarkRead({ slug }) {
  useEffect(() => {
    markRead(slug);
  }, [slug]);
  return null;
}
