"use client";

import { useEffect, useRef, useState } from "react";
import { useTheme } from "next-themes";
import { Sun, BookOpen, Moon, Type } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import {
  READING_SIZE_PX,
  setReadingSize,
  useReadingSize,
  type ReadingSize,
} from "@/lib/reader-prefs";

const THEMES: { value: string; label: string; icon: typeof Sun }[] = [
  { value: "light", label: "Paper", icon: Sun },
  { value: "sepia", label: "Sepia", icon: BookOpen },
  { value: "dark", label: "Ink", icon: Moon },
];

const SIZES: { value: ReadingSize; label: string; type: string }[] = [
  { value: "s", label: "Small", type: "text-[13px]" },
  { value: "m", label: "Medium", type: "text-[15px]" },
  { value: "l", label: "Large", type: "text-[18px]" },
];

export function ReaderSettings() {
  const { theme, setTheme } = useTheme();
  const size = useReadingSize();
  const [open, setOpen] = useState(false);
  const [mounted, setMounted] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => setMounted(true), []);

  useEffect(() => {
    if (!open) return;
    const onPointerDown = (e: PointerEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("pointerdown", onPointerDown);
    window.addEventListener("keydown", onKeyDown);
    return () => {
      window.removeEventListener("pointerdown", onPointerDown);
      window.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  const activeTheme = mounted ? theme ?? "light" : "light";

  return (
    <div ref={ref} className="relative">
      <Button
        variant="ghost"
        size="icon-sm"
        aria-label="Reading settings"
        aria-haspopup="dialog"
        aria-expanded={open}
        onClick={() => setOpen((v) => !v)}
      >
        <Type className="size-4" />
      </Button>

      {open ? (
        <div
          role="dialog"
          aria-label="Reading settings"
          className="shadow-overlay absolute right-0 top-10 z-20 w-56 rounded-lg border border-border bg-popover p-3"
        >
          <p className="mb-2 text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
            Theme
          </p>
          <div className="grid grid-cols-3 gap-1.5">
            {THEMES.map(({ value, label, icon: Icon }) => (
              <button
                key={value}
                type="button"
                aria-pressed={activeTheme === value}
                onClick={() => setTheme(value)}
                className={cn(
                  "flex flex-col items-center gap-1 rounded-md border px-2 py-2 text-[12px] transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                  activeTheme === value
                    ? "border-accent bg-surface-muted text-foreground"
                    : "border-border text-muted-foreground hover:bg-surface-muted/60"
                )}
              >
                <Icon className="size-4" />
                {label}
              </button>
            ))}
          </div>

          <p className="mb-2 mt-4 text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
            Text size
          </p>
          <div className="grid grid-cols-3 gap-1.5">
            {SIZES.map(({ value, label, type }) => (
              <button
                key={value}
                type="button"
                aria-pressed={size === value}
                aria-label={label}
                onClick={() => setReadingSize(value)}
                className={cn(
                  "flex items-center justify-center rounded-md border px-2 py-2 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                  type,
                  size === value
                    ? "border-accent bg-surface-muted text-foreground"
                    : "border-border text-muted-foreground hover:bg-surface-muted/60"
                )}
              >
                <span className="font-[family-name:var(--font-reading)]">Aa</span>
              </button>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}

export function readingSizeStyle(size: ReadingSize): React.CSSProperties {
  return { ["--reading-size" as string]: READING_SIZE_PX[size] };
}
