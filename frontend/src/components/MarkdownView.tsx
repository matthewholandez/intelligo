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
      <TooltipContent side="top" className="shadow-overlay">
        {terms.length > 1 ? (
          <div className="flex flex-col gap-0.5">
            {terms.map((term) => (
              <span key={term}>{term}</span>
            ))}
          </div>
        ) : (
          terms[0] ?? ""
        )}
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
