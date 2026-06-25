"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  ArrowLeft,
  ChevronLeft,
  ChevronRight,
  Pencil,
  Save,
  X,
} from "lucide-react";
import { toast } from "sonner";
import { ConfirmDialog } from "@/components/ConfirmDialog";
import { ErrorState } from "@/components/ErrorState";
import { MarkdownView } from "@/components/MarkdownView";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import {
  useChapter,
  useChapters,
  useGlossary,
  useUpdateChapter,
} from "@/lib/hooks";
import { cn, isAxiosErrorWithStatus } from "@/lib/utils";

type ViewMode = "translation" | "side-by-side";

export default function ChapterReaderPage() {
  const params = useParams();
  const router = useRouter();
  const novelId = parseInt(params.id as string, 10);
  const chapId = parseInt(params.chap_id as string, 10);

  const { data: chapter, isLoading, isError, refetch, error } = useChapter(
    novelId,
    chapId
  );
  const { data: chapters } = useChapters(novelId);
  const { data: glossary } = useGlossary(novelId);
  const updateMutation = useUpdateChapter(novelId, chapId);

  const [viewMode, setViewMode] = useState<ViewMode>("translation");
  const [isEditing, setIsEditing] = useState(false);
  const [editBuffer, setEditBuffer] = useState("");
  const [savedText, setSavedText] = useState("");
  const [pendingNav, setPendingNav] = useState<string | null>(null);
  const [unsavedDialogOpen, setUnsavedDialogOpen] = useState(false);

  useEffect(() => {
    if (chapter) {
      const text = chapter.translated_text ?? "";
      setSavedText(text);
      if (!isEditing) {
        setEditBuffer(text);
      }
    }
  }, [chapter, isEditing]);

  const sortedChapters = useMemo(
    () => [...(chapters ?? [])].sort((a, b) => a.number - b.number),
    [chapters]
  );

  const currentIndex = sortedChapters.findIndex((ch) => ch.id === chapId);
  const prevChapter = currentIndex > 0 ? sortedChapters[currentIndex - 1] : null;
  const nextChapter =
    currentIndex >= 0 && currentIndex < sortedChapters.length - 1
      ? sortedChapters[currentIndex + 1]
      : null;

  const hasUnsavedChanges =
    isEditing && editBuffer !== (chapter?.translated_text ?? "");

  const navigate = useCallback(
    (href: string) => {
      if (hasUnsavedChanges) {
        setPendingNav(href);
        setUnsavedDialogOpen(true);
        return;
      }
      router.push(href);
    },
    [hasUnsavedChanges, router]
  );

  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if (isEditing) return;
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }
      if (e.key === "ArrowLeft" && prevChapter) {
        navigate(`/novels/${novelId}/chapters/${prevChapter.id}`);
      }
      if (e.key === "ArrowRight" && nextChapter) {
        navigate(`/novels/${novelId}/chapters/${nextChapter.id}`);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [isEditing, navigate, nextChapter, novelId, prevChapter]);

  const startEditing = () => {
    setEditBuffer(chapter?.translated_text ?? "");
    setIsEditing(true);
  };

  const cancelEditing = () => {
    setEditBuffer(savedText);
    setIsEditing(false);
  };

  const saveEditing = async () => {
    try {
      await updateMutation.mutateAsync({ translated_text: editBuffer });
      toast.success("Saved");
      setSavedText(editBuffer);
      setIsEditing(false);
    } catch {
      // toast handled in hook
    }
  };

  const confirmDiscard = () => {
    setUnsavedDialogOpen(false);
    setIsEditing(false);
    if (pendingNav) {
      router.push(pendingNav);
      setPendingNav(null);
    }
  };

  if (isLoading) {
    return (
      <ReaderShell novelId={novelId} chapterNumber={null}>
        <Skeleton className="h-8 w-48" />
        <Skeleton className="mt-8 h-64 w-full" />
      </ReaderShell>
    );
  }

  if (isError || !chapter) {
    const is404 = isAxiosErrorWithStatus(error, 404);
    return (
      <ReaderShell novelId={novelId} chapterNumber={null}>
        <ErrorState
          message={is404 ? "Chapter not found." : "Something went wrong loading this chapter."}
          onRetry={is404 ? undefined : () => refetch()}
        />
        <Link
          href={`/novels/${novelId}`}
          className="mt-4 inline-block text-sm text-accent underline underline-offset-2"
        >
          Back to dashboard
        </Link>
      </ReaderShell>
    );
  }

  const translationPanel = isEditing ? (
    <div className="flex h-full min-h-[50vh] flex-col">
      <Textarea
        value={editBuffer}
        onChange={(e) => setEditBuffer(e.target.value)}
        className="min-h-[50vh] flex-1 resize-none rounded-lg border-border font-mono text-sm leading-relaxed"
        style={{ whiteSpace: "pre" }}
      />
      <div className="mt-3 flex gap-2">
        <Button
          size="sm"
          disabled={!hasUnsavedChanges || updateMutation.isPending}
          onClick={saveEditing}
        >
          <Save className="size-3.5" />
          Save
        </Button>
        <Button size="sm" variant="outline" onClick={cancelEditing}>
          <X className="size-3.5" />
          Cancel
        </Button>
      </div>
    </div>
  ) : chapter.translated_text != null ? (
    <MarkdownView content={chapter.translated_text} glossary={glossary ?? []} />
  ) : (
    <p className="rounded-lg border border-border bg-surface-muted px-4 py-6 text-muted-foreground">
      This chapter hasn&apos;t been translated.
    </p>
  );

  return (
    <>
      <div className="sticky top-0 z-10 border-b border-border bg-background">
        <div
          className={cn(
            "mx-auto flex h-14 items-center gap-3 px-4 sm:px-6",
            viewMode === "translation" ? "max-w-[680px]" : "max-w-[1100px]"
          )}
        >
          <Button
            variant="ghost"
            size="icon-sm"
            aria-label="Back to dashboard"
            onClick={() => navigate(`/novels/${novelId}`)}
          >
            <ArrowLeft className="size-4" />
          </Button>
          <span className="font-medium">Ch. {chapter.number}</span>
          <div className="flex-1" />
          <ToggleGroup
            value={[viewMode]}
            onValueChange={(values) => {
              const next = values[0] as ViewMode | undefined;
              if (next) setViewMode(next);
            }}
            variant="outline"
            spacing={0}
          >
            <ToggleGroupItem value="translation" aria-label="Translation view">
              Translation
            </ToggleGroupItem>
            <ToggleGroupItem value="side-by-side" aria-label="Side-by-side view">
              Side-by-side
            </ToggleGroupItem>
          </ToggleGroup>
          {!isEditing ? (
            <Button variant="outline" size="sm" onClick={startEditing}>
              <Pencil className="size-3.5" />
              Edit
            </Button>
          ) : null}
          <Button
            variant="ghost"
            size="icon-sm"
            aria-label="Previous chapter"
            disabled={!prevChapter}
            onClick={() =>
              prevChapter &&
              navigate(`/novels/${novelId}/chapters/${prevChapter.id}`)
            }
          >
            <ChevronLeft className="size-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon-sm"
            aria-label="Next chapter"
            disabled={!nextChapter}
            onClick={() =>
              nextChapter &&
              navigate(`/novels/${novelId}/chapters/${nextChapter.id}`)
            }
          >
            <ChevronRight className="size-4" />
          </Button>
        </div>
      </div>

      {viewMode === "translation" ? (
        <div className="mx-auto w-full max-w-[680px] px-4 py-8 sm:px-6">
          {translationPanel}
        </div>
      ) : (
        <div className="mx-auto w-full max-w-[1100px] px-4 py-8 sm:px-6">
          <div className="flex flex-col gap-8 min-[900px]:flex-row min-[900px]:gap-8">
            <section className="min-h-[40vh] flex-1 min-[900px]:overflow-y-auto">
              <h2 className="mb-3 text-[13px] font-medium text-muted-foreground">
                Source
              </h2>
              <pre className="whitespace-pre-wrap rounded-lg bg-surface-muted p-4 font-mono text-sm leading-relaxed text-foreground">
                {chapter.source_text}
              </pre>
            </section>
            <div className="hidden w-px shrink-0 bg-border min-[900px]:block" />
            <section className="min-h-[40vh] flex-1 min-[900px]:overflow-y-auto">
              <h2 className="mb-3 text-[13px] font-medium text-muted-foreground">
                Translation
              </h2>
              {translationPanel}
            </section>
          </div>
        </div>
      )}

      <ConfirmDialog
        open={unsavedDialogOpen}
        onOpenChange={setUnsavedDialogOpen}
        title="Discard unsaved changes?"
        description="You have unsaved edits to this translation. Leave without saving?"
        confirmLabel="Discard"
        destructive
        onConfirm={confirmDiscard}
      />
    </>
  );
}

function ReaderShell({
  novelId,
  chapterNumber,
  children,
}: {
  novelId: number;
  chapterNumber: number | null;
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-background">
      <div className="border-b border-border">
        <div className="mx-auto flex h-14 max-w-[1100px] items-center gap-3 px-4 sm:px-6">
          <Link href={`/novels/${novelId}`}>
            <Button variant="ghost" size="icon-sm" aria-label="Back to dashboard">
              <ArrowLeft className="size-4" />
            </Button>
          </Link>
          {chapterNumber != null ? (
            <span className="font-medium">Ch. {chapterNumber}</span>
          ) : null}
        </div>
      </div>
      <div className="mx-auto max-w-[680px] px-4 py-8 sm:px-6">{children}</div>
    </div>
  );
}
