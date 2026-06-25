"use client";

import { useSyncExternalStore } from "react";

export type ReadingSize = "s" | "m" | "l";

export const READING_SIZE_PX: Record<ReadingSize, string> = {
  s: "17px",
  m: "19px",
  l: "22px",
};

const STORAGE_KEY = "intelligo:reading-size";
const listeners = new Set<() => void>();
let current: ReadingSize = "m";
let hydrated = false;

function hydrate() {
  if (hydrated || typeof window === "undefined") return;
  const stored = window.localStorage.getItem(STORAGE_KEY) as ReadingSize | null;
  if (stored === "s" || stored === "m" || stored === "l") current = stored;
  hydrated = true;
}

export function setReadingSize(size: ReadingSize) {
  current = size;
  if (typeof window !== "undefined") {
    window.localStorage.setItem(STORAGE_KEY, size);
  }
  listeners.forEach((l) => l());
}

function subscribe(listener: () => void) {
  hydrate();
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function useReadingSize(): ReadingSize {
  return useSyncExternalStore(
    subscribe,
    () => {
      hydrate();
      return current;
    },
    () => "m"
  );
}
