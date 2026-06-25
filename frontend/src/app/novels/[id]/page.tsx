"use client";

import Link from "next/link";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { useCallback, useState } from "react";
import { ArrowLeft, Pencil } from "lucide-react";
import { toast } from "sonner";
import { AppShell } from "@/components/AppShell";
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useNovel, useUpdateNovel } from "@/lib/hooks";
import { isAxiosErrorWithStatus } from "@/lib/utils";
import ChaptersTab from "./ChaptersTab";
import GlossaryTab from "./GlossaryTab";

export default function NovelDashboardPage() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const novelId = parseInt(params.id as string, 10);

  const tabParam = searchParams.get("tab");
  const activeTab = tabParam === "glossary" ? "glossary" : "chapters";

  const { data: novel, isLoading, isError, refetch, error } = useNovel(novelId);
  const updateMutation = useUpdateNovel(novelId);

  const [renameOpen, setRenameOpen] = useState(false);
  const [renameName, setRenameName] = useState("");

  const setTab = useCallback(
    (tab: string) => {
      const url = tab === "chapters"
        ? `/novels/${novelId}`
        : `/novels/${novelId}?tab=${tab}`;
      router.replace(url);
    },
    [novelId, router]
  );

  const handleRename = async () => {
    const name = renameName.trim();
    if (!name || !novel || name === novel.name) {
      setRenameOpen(false);
      return;
    }
    await updateMutation.mutateAsync({ name });
    toast.success("Novel renamed");
    setRenameOpen(false);
  };

  if (isLoading) {
    return (
      <AppShell>
        <Skeleton className="mb-4 h-4 w-32" />
        <Skeleton className="mb-8 h-8 w-64" />
        <Skeleton className="h-10 w-full max-w-md" />
      </AppShell>
    );
  }

  if (isError || !novel) {
    const is404 = isAxiosErrorWithStatus(error, 404);

    return (
      <AppShell>
        <ErrorState
          message={
            is404
              ? "Novel not found."
              : "Something went wrong loading this novel."
          }
          onRetry={is404 ? undefined : () => refetch()}
        />
        <Link
          href="/"
          className="mt-4 inline-block text-sm text-accent underline underline-offset-2"
        >
          Back to library
        </Link>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="mb-6">
        <Link
          href="/"
          className="inline-flex items-center gap-1 text-sm text-muted-foreground transition-colors duration-150 hover:text-foreground"
        >
          <ArrowLeft className="size-4" />
          Back to library
        </Link>
      </div>

      <div className="mb-8 flex items-start justify-between gap-4">
        <div>
          <h1 className="font-heading text-[28px] font-semibold leading-tight">{novel.name}</h1>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => {
            setRenameName(novel.name);
            setRenameOpen(true);
          }}
        >
          <Pencil className="size-3.5" />
          Rename
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={setTab}>
        <TabsList className="mb-6">
          <TabsTrigger value="chapters">Chapters</TabsTrigger>
          <TabsTrigger value="glossary">Glossary</TabsTrigger>
        </TabsList>
        <TabsContent value="chapters">
          <ChaptersTab novelId={novelId} />
        </TabsContent>
        <TabsContent value="glossary">
          <GlossaryTab novelId={novelId} />
        </TabsContent>
      </Tabs>

      <Dialog open={renameOpen} onOpenChange={setRenameOpen}>
        <DialogContent className="shadow-overlay sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Rename novel</DialogTitle>
          </DialogHeader>
          <div className="space-y-2">
            <Label htmlFor="dashboard-rename">Name</Label>
            <Input
              id="dashboard-rename"
              value={renameName}
              autoFocus
              onChange={(e) => setRenameName(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleRename();
              }}
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setRenameOpen(false)}>
              Cancel
            </Button>
            <Button
              disabled={
                !renameName.trim() ||
                renameName.trim() === novel.name ||
                updateMutation.isPending
              }
              onClick={handleRename}
            >
              Save
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AppShell>
  );
}
