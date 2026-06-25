"use client";

import { useEffect, useRef, useState } from "react";
import { Upload } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { useChapters, useUploadChapter } from "@/lib/hooks";
import { cn, getErrorMessage } from "@/lib/utils";

const MAX_FILE_SIZE = 5 * 1024 * 1024;

type SourceMode = "file" | "paste";

type UploadChapterDialogProps = {
  novelId: number;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: (chapterId: number, chapterNumber: number) => void;
};

export function UploadChapterDialog({
  novelId,
  open,
  onOpenChange,
  onSuccess,
}: UploadChapterDialogProps) {
  const { data: chapters } = useChapters(novelId);
  const uploadMutation = useUploadChapter(novelId);

  const [number, setNumber] = useState("");
  const [sourceMode, setSourceMode] = useState<SourceMode>("file");
  const [file, setFile] = useState<File | null>(null);
  const [sourceText, setSourceText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!open) return;
    const maxNumber = chapters?.reduce((max, ch) => Math.max(max, ch.number), -1) ?? -1;
    setNumber(String(maxNumber + 1));
    setSourceMode("file");
    setFile(null);
    setSourceText("");
    setError(null);
  }, [open, chapters]);

  const validate = (): string | null => {
    const num = Number(number);
    if (!Number.isInteger(num) || num < 0) {
      return "Chapter number must be a whole number of 0 or greater.";
    }
    if (sourceMode === "file") {
      if (!file) return "Please choose an HTML file or switch to paste text.";
      if (!file.name.toLowerCase().endsWith(".html")) {
        return "Only .html files are accepted.";
      }
      if (file.size > MAX_FILE_SIZE) {
        return "File must be 5 MB or smaller.";
      }
    } else if (!sourceText.trim()) {
      return "Please paste source text or switch to file upload.";
    }
    return null;
  };

  const handleSubmit = async () => {
    const validationError = validate();
    if (validationError) {
      setError(validationError);
      return;
    }

    setError(null);
    const num = parseInt(number, 10);

    try {
      const chapter = await uploadMutation.mutateAsync({
        number: num,
        file: sourceMode === "file" ? file ?? undefined : undefined,
        source_text: sourceMode === "paste" ? sourceText : undefined,
      });
      toast.success(`Chapter ${num} added — translating…`);
      onOpenChange(false);
      onSuccess?.(chapter.id, chapter.number);
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  const handleFile = (selected: File | null) => {
    if (!selected) return;
    if (!selected.name.toLowerCase().endsWith(".html")) {
      setError("Only .html files are accepted.");
      return;
    }
    if (selected.size > MAX_FILE_SIZE) {
      setError("File must be 5 MB or smaller.");
      return;
    }
    setFile(selected);
    setError(null);
  };

  const isPending = uploadMutation.isPending;

  return (
    <Dialog open={open} onOpenChange={(next) => !isPending && onOpenChange(next)}>
      <DialogContent
        className="shadow-overlay max-h-[85vh] overflow-y-auto sm:max-w-lg"
        showCloseButton={!isPending}
      >
        <DialogHeader>
          <DialogTitle>Upload chapter</DialogTitle>
          <DialogDescription>
            Add an .html file or paste source text. Translation starts
            automatically and runs in the background.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="chapter-number">Chapter number</Label>
            <Input
              id="chapter-number"
              type="number"
              min={0}
              step={1}
              value={number}
              disabled={isPending}
              onChange={(e) => setNumber(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label>Source</Label>
            <ToggleGroup
              value={[sourceMode]}
              onValueChange={(values) => {
                const next = values[0] as SourceMode | undefined;
                if (next) {
                  setSourceMode(next);
                  setError(null);
                }
              }}
              variant="outline"
              spacing={0}
              disabled={isPending}
            >
              <ToggleGroupItem value="file" aria-label="Upload file">
                File
              </ToggleGroupItem>
              <ToggleGroupItem value="paste" aria-label="Paste text">
                Paste
              </ToggleGroupItem>
            </ToggleGroup>
          </div>

          {sourceMode === "file" ? (
            <div
              className={cn(
                "flex flex-col items-center justify-center rounded-lg border border-dashed border-border px-4 py-8 transition-colors duration-150",
                dragOver && "border-accent bg-surface-muted",
                isPending && "opacity-60"
              )}
              onDragOver={(e) => {
                e.preventDefault();
                setDragOver(true);
              }}
              onDragLeave={() => setDragOver(false)}
              onDrop={(e) => {
                e.preventDefault();
                setDragOver(false);
                if (isPending) return;
                handleFile(e.dataTransfer.files[0] ?? null);
              }}
            >
              <Upload className="mb-2 size-5 text-muted-foreground" />
              <p className="text-sm text-muted-foreground">
                Drag and drop an HTML file, or{" "}
                <button
                  type="button"
                  className="text-accent underline underline-offset-2"
                  disabled={isPending}
                  onClick={() => fileInputRef.current?.click()}
                >
                  browse
                </button>
              </p>
              <p className="mt-1 text-xs text-muted-foreground">.html only, up to 5 MB</p>
              {file ? (
                <p className="mt-3 text-sm font-medium">{file.name}</p>
              ) : null}
              <input
                ref={fileInputRef}
                type="file"
                accept=".html,text/html"
                className="hidden"
                disabled={isPending}
                onChange={(e) => handleFile(e.target.files?.[0] ?? null)}
              />
            </div>
          ) : (
            <Textarea
              placeholder="Paste chapter source text…"
              value={sourceText}
              disabled={isPending}
              onChange={(e) => setSourceText(e.target.value)}
              className="max-h-[45vh] min-h-[160px] font-mono text-sm"
            />
          )}

          {error ? (
            <p className="text-sm text-destructive" role="alert">
              {error}
            </p>
          ) : null}
        </div>

        <DialogFooter>
          <Button variant="outline" disabled={isPending} onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          {error && !isPending ? (
            <Button onClick={handleSubmit}>Retry</Button>
          ) : (
            <Button disabled={isPending} onClick={handleSubmit}>
              {isPending ? "Uploading…" : "Upload chapter"}
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
