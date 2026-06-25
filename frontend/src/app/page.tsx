"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Pencil, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { AppShell } from "@/components/AppShell";
import { ConfirmDialog } from "@/components/ConfirmDialog";
import { EmptyState } from "@/components/EmptyState";
import { ErrorState } from "@/components/ErrorState";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import {
  useCreateNovel,
  useDeleteNovel,
  useNovels,
  useUpdateNovel,
} from "@/lib/hooks";
import { formatRelativeTime } from "@/lib/utils";
import type { Novel } from "@/types";

function NovelCardSkeleton() {
  return (
    <div className="rounded-lg border border-border p-5">
      <Skeleton className="h-5 w-2/3" />
      <Skeleton className="mt-3 h-4 w-1/3" />
    </div>
  );
}

function NovelCard({
  novel,
  onRename,
  onDelete,
}: {
  novel: Novel;
  onRename: (novel: Novel) => void;
  onDelete: (novel: Novel) => void;
}) {
  return (
    <div className="group relative rounded-lg border border-border bg-surface transition-all duration-150 hover:border-accent/40 hover:shadow-overlay">
      <Link
        href={`/novels/${novel.id}`}
        className="block p-5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded-lg"
      >
        <h2 className="font-heading text-lg font-semibold leading-snug text-foreground">
          {novel.name}
        </h2>
        <p className="mt-2 text-[12px] text-muted-foreground">
          Updated {formatRelativeTime(novel.updated_on)}
        </p>
      </Link>
      <div className="absolute right-3 top-3 flex gap-1 opacity-0 transition-opacity duration-150 group-hover:opacity-100 group-focus-within:opacity-100">
        <Button
          variant="ghost"
          size="icon-sm"
          aria-label={`Rename ${novel.name}`}
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            onRename(novel);
          }}
        >
          <Pencil className="size-3.5" />
        </Button>
        <Button
          variant="ghost"
          size="icon-sm"
          aria-label={`Delete ${novel.name}`}
          className="text-destructive hover:text-destructive"
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            onDelete(novel);
          }}
        >
          <Trash2 className="size-3.5" />
        </Button>
      </div>
    </div>
  );
}

export default function LibraryPage() {
  const router = useRouter();
  const { data: novels, isLoading, isError, refetch } = useNovels();
  const createMutation = useCreateNovel();

  const [newDialogOpen, setNewDialogOpen] = useState(false);
  const [newName, setNewName] = useState("");
  const [renameTarget, setRenameTarget] = useState<Novel | null>(null);
  const [renameName, setRenameName] = useState("");
  const [deleteTarget, setDeleteTarget] = useState<Novel | null>(null);

  const renameMutation = useUpdateNovel(renameTarget?.id ?? 0);
  const deleteMutation = useDeleteNovel();

  const handleCreate = async () => {
    const name = newName.trim();
    if (!name) return;
    const novel = await createMutation.mutateAsync({ name });
    toast.success("Novel created");
    setNewDialogOpen(false);
    setNewName("");
    router.push(`/novels/${novel.id}`);
  };

  const handleRename = async () => {
    if (!renameTarget) return;
    const name = renameName.trim();
    if (!name || name === renameTarget.name) {
      setRenameTarget(null);
      return;
    }
    await renameMutation.mutateAsync({ name });
    toast.success("Novel renamed");
    setRenameTarget(null);
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    await deleteMutation.mutateAsync(deleteTarget.id);
    toast.success("Novel deleted");
    setDeleteTarget(null);
  };

  return (
    <AppShell
      headerRight={
        <Button onClick={() => setNewDialogOpen(true)}>New novel</Button>
      }
    >
      <div className="mb-8">
        <h1 className="font-heading text-[28px] font-semibold leading-tight">
          Library
        </h1>
        <p className="mt-1 text-[13px] font-medium text-muted-foreground">
          Your novels, each with its own glossary of names and terms.
        </p>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <NovelCardSkeleton key={i} />
          ))}
        </div>
      ) : isError ? (
        <ErrorState onRetry={() => refetch()} />
      ) : novels?.length === 0 ? (
        <EmptyState
          message="No novels yet. Create one to get started."
          actionLabel="New novel"
          onAction={() => setNewDialogOpen(true)}
        />
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {novels?.map((novel) => (
            <NovelCard
              key={novel.id}
              novel={novel}
              onRename={(n) => {
                setRenameTarget(n);
                setRenameName(n.name);
              }}
              onDelete={setDeleteTarget}
            />
          ))}
        </div>
      )}

      <Dialog open={newDialogOpen} onOpenChange={setNewDialogOpen}>
        <DialogContent className="shadow-overlay sm:max-w-md">
          <DialogHeader>
            <DialogTitle>New novel</DialogTitle>
          </DialogHeader>
          <div className="space-y-2">
            <Label htmlFor="novel-name">Name</Label>
            <Input
              id="novel-name"
              value={newName}
              autoFocus
              placeholder="Novel title"
              onChange={(e) => setNewName(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleCreate();
              }}
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setNewDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              disabled={!newName.trim() || createMutation.isPending}
              onClick={handleCreate}
            >
              Create
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog
        open={!!renameTarget}
        onOpenChange={(open) => !open && setRenameTarget(null)}
      >
        <DialogContent className="shadow-overlay sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Rename novel</DialogTitle>
          </DialogHeader>
          <div className="space-y-2">
            <Label htmlFor="rename-novel">Name</Label>
            <Input
              id="rename-novel"
              value={renameName}
              autoFocus
              onChange={(e) => setRenameName(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleRename();
              }}
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setRenameTarget(null)}>
              Cancel
            </Button>
            <Button
              disabled={
                !renameName.trim() ||
                renameName.trim() === renameTarget?.name ||
                renameMutation.isPending
              }
              onClick={handleRename}
            >
              Save
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={!!deleteTarget}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
        title="Delete novel"
        description={
          <>
            Delete <strong>{deleteTarget?.name}</strong> and all its chapters and
            glossary? This can&apos;t be undone.
          </>
        }
        confirmLabel="Delete"
        destructive
        isPending={deleteMutation.isPending}
        onConfirm={handleDelete}
      />
    </AppShell>
  );
}
