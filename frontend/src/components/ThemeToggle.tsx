"use client";

import { useEffect, useState } from "react";
import { useTheme } from "next-themes";
import { Sun, BookOpen, Moon } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

const ORDER = ["light", "sepia", "dark"] as const;
const META: Record<(typeof ORDER)[number], { icon: typeof Sun; label: string }> = {
  light: { icon: Sun, label: "Paper" },
  sepia: { icon: BookOpen, label: "Sepia" },
  dark: { icon: Moon, label: "Ink" },
};

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  const active = (mounted ? theme : "light") ?? "light";
  const current = (ORDER as readonly string[]).includes(active)
    ? (active as (typeof ORDER)[number])
    : "light";
  const next = ORDER[(ORDER.indexOf(current) + 1) % ORDER.length];
  const Icon = META[current].icon;

  return (
    <Tooltip>
      <TooltipTrigger
        render={
          <Button
            variant="ghost"
            size="icon-sm"
            aria-label={`Theme: ${META[current].label}. Switch to ${META[next].label}.`}
            onClick={() => setTheme(next)}
          />
        }
      >
        <Icon className="size-4" />
      </TooltipTrigger>
      <TooltipContent side="bottom">{META[current].label} · switch to {META[next].label}</TooltipContent>
    </Tooltip>
  );
}
