"use client";

import { useMemo, useState } from "react";
import { Check, Pencil, Trash2, X } from "lucide-react";
import { ConfirmDialog } from "@/components/ConfirmDialog";
import { EmptyState } from "@/components/EmptyState";
import { ErrorState } from "@/components/ErrorState";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  useCreateGlossaryEntry,
  useDeleteGlossaryEntry,
  useGlossary,
  useUpdateGlossaryEntry,
  isAxiosErrorWithStatus,
} from "@/lib/hooks";
import type { GlossaryEntry } from "@/types";

type EditState = {
  id?: number;
  source_term: string;
  translation: string;
  isNew?: boolean;
};

function GlossaryRowSkeleton() {
  return (
    <TableRow>
      <TableCell><Skeleton className="h-8 w-full" /></TableCell>
      <TableCell><Skeleton className="h-8 w-full" /></TableCell>
      <TableCell><Skeleton className="h-8 w-16" /></TableCell>
    </TableRow>
  );
}

export default function GlossaryTab({ novelId }: { novelId: number }) {
  const { data: glossary, isLoading, isError, refetch } = useGlossary(novelId);
  const createMutation = useCreateGlossaryEntry(novelId);
  const updateMutation = useUpdateGlossaryEntry(novelId);
  const deleteMutation = useDeleteGlossaryEntry(novelId);

  const [search, setSearch] = useState("");
  const [editing, setEditing] = useState<EditState | null>(null);
  const [sourceError, setSourceError] = useState<string | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<GlossaryEntry | null>(null);

  const filtered = useMemo(() => {
    if (!glossary) return [];
    const q = search.trim().toLowerCase();
    if (!q) return glossary;
    return glossary.filter(
      (entry) =>
        entry.source_term.toLowerCase().includes(q) ||
        entry.translation.toLowerCase().includes(q)
    );
  }, [glossary, search]);

  const startEdit = (entry: GlossaryEntry) => {
    setSourceError(null);
    setEditing({
      id: entry.id,
      source_term: entry.source_term,
      translation: entry.translation,
    });
  };

  const startAdd = () => {
    setSourceError(null);
    setEditing({ source_term: "", translation: "", isNew: true });
  };

  const cancelEdit = () => {
    setEditing(null);
    setSourceError(null);
  };

  const saveEdit = async () => {
    if (!editing) return;
    const source_term = editing.source_term.trim();
    const translation = editing.translation.trim();
    if (!source_term || !translation) return;

    setSourceError(null);

    try {
      if (editing.isNew) {
        await createMutation.mutateAsync({ source_term, translation });
      } else if (editing.id != null) {
        await updateMutation.mutateAsync({
          entryId: editing.id,
          entry: { source_term, translation },
        });
      }
      setEditing(null);
    } catch (error) {
      if (isAxiosErrorWithStatus(error, 409)) {
        setSourceError("A term with this source already exists.");
      }
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    await deleteMutation.mutateAsync(deleteTarget.id);
    setDeleteTarget(null);
  };

  const isSaving = createMutation.isPending || updateMutation.isPending;

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <Input
          placeholder="Search terms…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-xs"
        />
        <Button onClick={startAdd} disabled={!!editing?.isNew}>
          Add term
        </Button>
      </div>

      {isLoading ? (
        <div className="rounded-lg border border-border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Source term</TableHead>
                <TableHead>Translation</TableHead>
                <TableHead className="w-[100px]" />
              </TableRow>
            </TableHeader>
            <TableBody>
              {Array.from({ length: 4 }).map((_, i) => (
                <GlossaryRowSkeleton key={i} />
              ))}
            </TableBody>
          </Table>
        </div>
      ) : isError ? (
        <ErrorState onRetry={() => refetch()} />
      ) : glossary?.length === 0 && !editing?.isNew ? (
        <EmptyState
          message="No glossary terms yet. Terms are added automatically as you translate, or add them by hand."
          actionLabel="Add term"
          onAction={startAdd}
        />
      ) : (
        <div className="overflow-x-auto rounded-lg border border-border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Source term</TableHead>
                <TableHead>Translation</TableHead>
                <TableHead className="w-[100px] text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {editing?.isNew ? (
                <TableRow>
                  <TableCell>
                    <Input
                      value={editing.source_term}
                      autoFocus
                      aria-invalid={!!sourceError}
                      onChange={(e) =>
                        setEditing({ ...editing, source_term: e.target.value })
                      }
                    />
                    {sourceError ? (
                      <p className="mt-1 text-xs text-destructive">{sourceError}</p>
                    ) : null}
                  </TableCell>
                  <TableCell>
                    <Input
                      value={editing.translation}
                      onChange={(e) =>
                        setEditing({ ...editing, translation: e.target.value })
                      }
                    />
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-1">
                      <Button
                        variant="ghost"
                        size="icon-sm"
                        aria-label="Save term"
                        disabled={isSaving}
                        onClick={saveEdit}
                      >
                        <Check className="size-3.5" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon-sm"
                        aria-label="Cancel"
                        onClick={cancelEdit}
                      >
                        <X className="size-3.5" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ) : null}

              {filtered.map((entry) => {
                const isEditing = editing?.id === entry.id && !editing.isNew;
                return (
                  <TableRow key={entry.id}>
                    <TableCell>
                      {isEditing ? (
                        <>
                          <Input
                            value={editing.source_term}
                            aria-invalid={!!sourceError}
                            onChange={(e) =>
                              setEditing({ ...editing, source_term: e.target.value })
                            }
                          />
                          {sourceError ? (
                            <p className="mt-1 text-xs text-destructive">{sourceError}</p>
                          ) : null}
                        </>
                      ) : (
                        <span className="font-medium">{entry.source_term}</span>
                      )}
                    </TableCell>
                    <TableCell>
                      {isEditing ? (
                        <Input
                          value={editing.translation}
                          onChange={(e) =>
                            setEditing({ ...editing, translation: e.target.value })
                          }
                        />
                      ) : (
                        entry.translation
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      {isEditing ? (
                        <div className="flex justify-end gap-1">
                          <Button
                            variant="ghost"
                            size="icon-sm"
                            aria-label="Save changes"
                            disabled={isSaving}
                            onClick={saveEdit}
                          >
                            <Check className="size-3.5" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon-sm"
                            aria-label="Cancel editing"
                            onClick={cancelEdit}
                          >
                            <X className="size-3.5" />
                          </Button>
                        </div>
                      ) : (
                        <div className="flex justify-end gap-1">
                          <Button
                            variant="ghost"
                            size="icon-sm"
                            aria-label={`Edit ${entry.source_term}`}
                            disabled={!!editing}
                            onClick={() => startEdit(entry)}
                          >
                            <Pencil className="size-3.5" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon-sm"
                            aria-label={`Delete ${entry.source_term}`}
                            className="text-destructive"
                            disabled={!!editing}
                            onClick={() => setDeleteTarget(entry)}
                          >
                            <Trash2 className="size-3.5" />
                          </Button>
                        </div>
                      )}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>
      )}

      <ConfirmDialog
        open={!!deleteTarget}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
        title="Delete glossary term"
        description={
          <>
            Delete <strong>{deleteTarget?.source_term}</strong>? This can&apos;t be
            undone.
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
