"use client";

import {
  useMutation,
  useQuery,
  useQueryClient,
  type UseQueryResult,
} from "@tanstack/react-query";
import { toast } from "sonner";
import {
  createGlossaryEntry,
  createNovel,
  deleteChapter,
  deleteGlossaryEntry,
  deleteNovel,
  getChapter,
  getNovel,
  listChapters,
  listGlossary,
  listNovels,
  retranslateChapter,
  updateChapter,
  updateGlossaryEntry,
  updateNovel,
  uploadChapter,
} from "@/lib/api";
import { queryKeys } from "@/lib/queryKeys";
import { getErrorMessage, isAxiosErrorWithStatus } from "@/lib/utils";
import type {
  Chapter,
  ChapterStatus,
  ChapterUpdate,
  GlossaryEntry,
  GlossaryEntryCreate,
  GlossaryEntryUpdate,
  Novel,
  NovelCreate,
  NovelUpdate,
} from "@/types";

const STALE_TIME = 30_000;
const POLL_INTERVAL = 1_500;

export function isChapterInProgress(status: ChapterStatus | undefined): boolean {
  return (
    status === "pending" || status === "analyzing" || status === "translating"
  );
}

function mutationErrorToast(error: unknown) {
  toast.error(getErrorMessage(error));
}

export function useNovels() {
  return useQuery({
    queryKey: queryKeys.novels,
    queryFn: () => listNovels(),
    staleTime: STALE_TIME,
  });
}

export function useNovel(id: number): UseQueryResult<Novel, Error> {
  return useQuery({
    queryKey: queryKeys.novel(id),
    queryFn: () => getNovel(id),
    staleTime: STALE_TIME,
    enabled: Number.isFinite(id),
  });
}

export function useChapters(novelId: number): UseQueryResult<Chapter[], Error> {
  return useQuery({
    queryKey: queryKeys.chapters(novelId),
    queryFn: () => listChapters(novelId),
    staleTime: STALE_TIME,
    enabled: Number.isFinite(novelId),
    refetchInterval: (query) =>
      query.state.data?.some((c) => isChapterInProgress(c.status))
        ? POLL_INTERVAL
        : false,
  });
}

export function useChapter(
  novelId: number,
  chapId: number
): UseQueryResult<Chapter, Error> {
  return useQuery({
    queryKey: queryKeys.chapter(novelId, chapId),
    queryFn: () => getChapter(novelId, chapId),
    staleTime: STALE_TIME,
    enabled: Number.isFinite(novelId) && Number.isFinite(chapId),
    refetchInterval: (query) =>
      isChapterInProgress(query.state.data?.status) ? POLL_INTERVAL : false,
  });
}

export function useGlossary(
  novelId: number
): UseQueryResult<GlossaryEntry[], Error> {
  return useQuery({
    queryKey: queryKeys.glossary(novelId),
    queryFn: () => listGlossary(novelId),
    staleTime: STALE_TIME,
    enabled: Number.isFinite(novelId),
  });
}

export function useCreateNovel() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (novel: NovelCreate) => createNovel(novel),
    retry: false,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.novels });
    },
    onError: mutationErrorToast,
  });
}

export function useUpdateNovel(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (novel: NovelUpdate) => updateNovel(id, novel),
    retry: false,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.novels });
      queryClient.invalidateQueries({ queryKey: queryKeys.novel(id) });
    },
    onError: mutationErrorToast,
  });
}

export function useDeleteNovel() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => deleteNovel(id),
    retry: false,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.novels });
    },
    onError: mutationErrorToast,
  });
}

export function useUploadChapter(novelId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: { number: number; file?: File; source_text?: string }) =>
      uploadChapter(novelId, payload.number, payload.file, payload.source_text),
    retry: false,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.chapters(novelId) });
    },
  });
}

export function useUpdateChapter(novelId: number, chapId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (update: ChapterUpdate) =>
      updateChapter(novelId, chapId, update),
    retry: false,
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.chapter(novelId, chapId),
      });
      queryClient.invalidateQueries({ queryKey: queryKeys.chapters(novelId) });
    },
    onError: mutationErrorToast,
  });
}

export function useRetranslateChapter(novelId: number, chapId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => retranslateChapter(novelId, chapId),
    retry: false,
    onSuccess: (chapter) => {
      queryClient.setQueryData(queryKeys.chapter(novelId, chapId), chapter);
      queryClient.invalidateQueries({ queryKey: queryKeys.chapters(novelId) });
    },
    onError: mutationErrorToast,
  });
}

export function useDeleteChapter(novelId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (chapId: number) => deleteChapter(novelId, chapId),
    retry: false,
    onSuccess: (_data, chapId) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.chapters(novelId) });
      queryClient.removeQueries({
        queryKey: queryKeys.chapter(novelId, chapId),
      });
    },
    onError: mutationErrorToast,
  });
}

export function useCreateGlossaryEntry(novelId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (entry: GlossaryEntryCreate) =>
      createGlossaryEntry(novelId, entry),
    retry: false,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.glossary(novelId) });
    },
    onError: (error) => {
      if (!isAxiosErrorWithStatus(error, 409)) {
        mutationErrorToast(error);
      }
    },
  });
}

export function useUpdateGlossaryEntry(novelId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      entryId,
      entry,
    }: {
      entryId: number;
      entry: GlossaryEntryUpdate;
    }) => updateGlossaryEntry(novelId, entryId, entry),
    retry: false,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.glossary(novelId) });
    },
    onError: (error) => {
      if (!isAxiosErrorWithStatus(error, 409)) {
        mutationErrorToast(error);
      }
    },
  });
}

export function useDeleteGlossaryEntry(novelId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (entryId: number) => deleteGlossaryEntry(novelId, entryId),
    retry: false,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.glossary(novelId) });
    },
    onError: mutationErrorToast,
  });
}

export { isAxiosErrorWithStatus };
