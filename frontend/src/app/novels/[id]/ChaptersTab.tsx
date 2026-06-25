"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { ChevronRight, Loader2, Trash2 } from "lucide-react";
import { ConfirmDialog } from "@/components/ConfirmDialog";
import { EmptyState } from "@/components/EmptyState";
import { ErrorState } from "@/components/ErrorState";
import { UploadChapterDialog } from "@/components/UploadChapterDialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useChapters, useDeleteChapter } from "@/lib/hooks";
import { formatRelativeTime } from "@/lib/utils";
import type { Chapter } from "@/types";

const IN_PROGRESS_LABEL: Record<string, string> = {
  pending: "Queued…",
  analyzing: "Finding terms…",
  translating: "Translating…",
};

// Async translation moves through discrete stages with no numeric percent,
// so the bar reflects how far along the pipeline a chapter is.
const STAGE_FRACTION: Record<string, number> = {
  pending: 0.08,
  analyzing: 0.45,
  translating: 0.8,
};

function isInProgress(status: string) {
  return status in IN_PROGRESS_LABEL;
}

/** First meaningful line of text, skipping scene breaks and blank lines. */
function firstLine(text: string | null): string {
  if (!text) return "";
  for (const raw of text.split("\n")) {
    const line = raw.trim();
    if (line && !/^[*_\s.·]+$/.test(line)) return line;
  }
  return "";
}

function ChapterStatusIndicator({ chapter }: { chapter: Chapter }) {
  if (isInProgress(chapter.status)) {
    return (
      <span className="flex items-center gap-1.5 text-[13px] text-muted-foreground">
        <Loader2 className="size-3.5 animate-spin" />
        {IN_PROGRESS_LABEL[chapter.status]}
      </span>
    );
  }
  if (chapter.status === "failed") {
    return (
      <Badge variant="secondary" className="border-destructive/30 font-normal text-destructive">
        Failed
      </Badge>
    );
  }
  return <span className="text-[13px] text-muted-foreground">Translated</span>;
}

function ChapterProgress({ status }: { status: string }) {
  const fraction = STAGE_FRACTION[status] ?? 0;
  return (
    <div
      role="progressbar"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={Math.round(fraction * 100)}
      aria-label={IN_PROGRESS_LABEL[status]}
      className="h-1 w-full overflow-hidden rounded-full bg-border/70"
    >
      <div
        className="h-full rounded-full bg-accent transition-[width] duration-700 ease-out motion-safe:animate-pulse"
        style={{ width: `${fraction * 100}%` }}
      />
    </div>
  );
}

function ChapterRowSkeleton() {
  return (
    <div className="flex items-center gap-4 border-b border-border py-4 last:border-b-0">
      <Skeleton className="h-5 w-16" />
      <Skeleton className="h-5 w-24" />
      <Skeleton className="ml-auto h-5 w-20" />
    </div>
  );
}

export default function ChaptersTab({ novelId }: { novelId: number }) {
  const router = useRouter();
  const { data: chapters, isLoading, isError, refetch } = useChapters(novelId);
  const deleteMutation = useDeleteChapter(novelId);

  const [uploadOpen, setUploadOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<Chapter | null>(null);

  const handleDelete = async () => {
    if (!deleteTarget) return;
    await deleteMutation.mutateAsync(deleteTarget.id);
    setDeleteTarget(null);
  };

  const isEmpty = !isLoading && !isError && chapters?.length === 0;

  return (
    <div className="space-y-4">
      {!isEmpty ? (
        <div className="flex items-center justify-between gap-3">
          <span className="text-[13px] text-muted-foreground">
            {chapters
              ? `${chapters.length} ${chapters.length === 1 ? "chapter" : "chapters"}`
              : ""}
          </span>
          <Button onClick={() => setUploadOpen(true)}>Upload chapter</Button>
        </div>
      ) : null}

      {isLoading ? (
        <div className="rounded-lg border border-border px-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <ChapterRowSkeleton key={i} />
          ))}
        </div>
      ) : isError ? (
        <ErrorState onRetry={() => refetch()} />
      ) : chapters?.length === 0 ? (
        <EmptyState
          message="No chapters yet. Upload a chapter to begin translating."
          actionLabel="Upload chapter"
          onAction={() => setUploadOpen(true)}
        />
      ) : (
        <div className="rounded-lg border border-border divide-y divide-border">
          {chapters?.map((chapter) => {
            const inProgress = isInProgress(chapter.status);
            const preview = inProgress
              ? ""
              : firstLine(
                  chapter.status === "completed"
                    ? chapter.translated_text
                    : chapter.source_text
                );
            return (
            <div
              key={chapter.id}
              className="group flex items-center gap-3 px-4 py-3 transition-colors duration-150 hover:bg-surface-muted/60"
            >
              <Link
                href={`/novels/${novelId}/chapters/${chapter.id}`}
                className="flex min-w-0 flex-1 flex-col gap-1.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded-md"
              >
                <div className="flex items-center gap-3">
                  <span className="font-medium">Ch. {chapter.number}</span>
                  <ChapterStatusIndicator chapter={chapter} />
                  <span className="ml-auto text-[13px] font-medium text-muted-foreground">
                    {formatRelativeTime(chapter.updated_on)}
                  </span>
                  <ChevronRight className="size-4 shrink-0 text-muted-foreground opacity-0 transition-opacity duration-150 group-hover:opacity-100" />
                </div>
                {inProgress ? (
                  <ChapterProgress status={chapter.status} />
                ) : preview ? (
                  <p className="truncate text-[13px] text-muted-foreground">
                    {preview}
                  </p>
                ) : null}
              </Link>
              <Button
                variant="ghost"
                size="icon-sm"
                aria-label={`Delete chapter ${chapter.number}`}
                className="shrink-0 text-destructive opacity-0 transition-opacity duration-150 group-hover:opacity-100"
                onClick={() => setDeleteTarget(chapter)}
              >
                <Trash2 className="size-3.5" />
              </Button>
            </div>
            );
          })}
        </div>
      )}

      <UploadChapterDialog
        novelId={novelId}
        open={uploadOpen}
        onOpenChange={setUploadOpen}
        onSuccess={(chapterId) => {
          router.push(`/novels/${novelId}/chapters/${chapterId}`);
        }}
      />

      <ConfirmDialog
        open={!!deleteTarget}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
        title="Delete chapter"
        description={
          <>
            Delete chapter {deleteTarget?.number}? This can&apos;t be undone.
          </>
        }
        confirmLabel="Delete"
        destructive
        isPending={deleteMutation.isPending}
        onConfirm={handleDelete}
      />
    </div>
  );
}
