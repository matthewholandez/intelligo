"use client";

import { useMemo } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  createGlossaryHighlightPlugin,
  type GlossaryHighlightEntry,
} from "@/lib/glossary-highlight";
import { cn } from "@/lib/utils";

type MarkdownViewProps = {
  content: string;
  glossary?: GlossaryHighlightEntry[];
  className?: string;
};

function GlossaryMark({
  children,
  sourceTerms,
}: {
  children?: React.ReactNode;
  sourceTerms?: string;
}) {
  const terms = sourceTerms?.split("\n").filter(Boolean) ?? [];

  return (
    <Tooltip>
      <TooltipTrigger
        render={
          <mark className="glossary-highlight bg-transparent text-inherit" />
        }
      >
        {children}
      </TooltipTrigger>
      <TooltipContent
        side="top"
        className="shadow-overlay max-w-[260px] border border-border bg-popover px-3 py-2.5 text-popover-foreground"
      >
        <div className="flex items-start justify-between gap-3">
          <span className="text-[10px] font-medium uppercase tracking-[0.14em] text-muted-foreground">
            原文 · Source
          </span>
          {/* the seal: 印 = "mark / stamp" */}
          <span
            aria-hidden
            className="grid size-5 shrink-0 place-items-center rounded-[3px] border border-seal/70 font-source text-[11px] leading-none text-seal"
          >
            印
          </span>
        </div>
        <div className="mt-1.5 flex flex-col gap-1">
          {terms.length > 0 ? (
            terms.map((term) => (
              <span
                key={term}
                lang="zh"
                className="font-source text-[17px] leading-snug text-foreground"
              >
                {term}
              </span>
            ))
          ) : (
            <span className="text-sm text-muted-foreground">Glossary term</span>
          )}
        </div>
      </TooltipContent>
    </Tooltip>
  );
}

export function MarkdownView({
  content,
  glossary = [],
  className,
}: MarkdownViewProps) {
  const rehypePlugins = useMemo(() => {
    if (glossary.length === 0) return [];
    return [createGlossaryHighlightPlugin(glossary)];
  }, [glossary]);

  return (
    <div className={cn("reader-prose text-foreground", className)}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={rehypePlugins}
        components={{
          mark: ({ node, children, ...props }) => {
            const record = props as Record<string, unknown>;
            const sourceTerms =
              (record["data-source-terms"] as string | undefined) ??
              (record.dataSourceTerms as string | undefined) ??
              (node?.properties?.dataSourceTerms as string | undefined);
            return (
              <GlossaryMark sourceTerms={sourceTerms}>{children}</GlossaryMark>
            );
          },
          a: ({ href, children }) => (
            <a
              href={href}
              className="text-accent underline underline-offset-2 transition-colors duration-150 hover:text-foreground"
              target={href?.startsWith("http") ? "_blank" : undefined}
              rel={href?.startsWith("http") ? "noopener noreferrer" : undefined}
            >
              {children}
            </a>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
