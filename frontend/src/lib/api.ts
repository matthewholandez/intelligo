import axios from "axios";
import type {
  Chapter,
  ChapterUpdate,
  GlossaryEntry,
  GlossaryEntryCreate,
  GlossaryEntryUpdate,
  Novel,
  NovelCreate,
  NovelUpdate,
} from "@/types";

const api = axios.create({
  baseURL: "/api",
});

export const listNovels = async (
  offset = 0,
  limit = 100
): Promise<Novel[]> => {
  const { data } = await api.get("/novels", { params: { offset, limit } });
  return data;
};

export const getNovel = async (id: number): Promise<Novel> => {
  const { data } = await api.get(`/novels/${id}`);
  return data;
};

export const createNovel = async (novel: NovelCreate): Promise<Novel> => {
  const { data } = await api.post("/novels", novel);
  return data;
};

export const updateNovel = async (
  id: number,
  novel: NovelUpdate
): Promise<Novel> => {
  const { data } = await api.patch(`/novels/${id}`, novel);
  return data;
};

export const deleteNovel = async (id: number): Promise<void> => {
  await api.delete(`/novels/${id}`);
};

export const listChapters = async (novelId: number): Promise<Chapter[]> => {
  const { data } = await api.get(`/novels/${novelId}/chapters`);
  return data;
};

export const getChapter = async (
  novelId: number,
  chapterId: number
): Promise<Chapter> => {
  const { data } = await api.get(`/novels/${novelId}/chapters/${chapterId}`);
  return data;
};

export const uploadChapter = async (
  novelId: number,
  number: number,
  file?: File,
  source_text?: string
): Promise<Chapter> => {
  const formData = new FormData();
  formData.append("number", number.toString());
  if (file) {
    formData.append("file", file);
  } else if (source_text !== undefined) {
    formData.append("source_text", source_text);
  }
  const { data } = await api.post(`/novels/${novelId}/chapters`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
};

export const retranslateChapter = async (
  novelId: number,
  chapterId: number
): Promise<Chapter> => {
  const { data } = await api.post(
    `/novels/${novelId}/chapters/${chapterId}/retranslate`
  );
  return data;
};

export const updateChapter = async (
  novelId: number,
  chapterId: number,
  update: ChapterUpdate
): Promise<Chapter> => {
  const { data } = await api.patch(
    `/novels/${novelId}/chapters/${chapterId}`,
    update
  );
  return data;
};

export const deleteChapter = async (
  novelId: number,
  chapterId: number
): Promise<void> => {
  await api.delete(`/novels/${novelId}/chapters/${chapterId}`);
};

export const listGlossary = async (
  novelId: number
): Promise<GlossaryEntry[]> => {
  const { data } = await api.get(`/novels/${novelId}/glossary`);
  return data;
};

export const createGlossaryEntry = async (
  novelId: number,
  entry: GlossaryEntryCreate
): Promise<GlossaryEntry> => {
  const { data } = await api.post(`/novels/${novelId}/glossary`, entry);
  return data;
};

export const updateGlossaryEntry = async (
  novelId: number,
  entryId: number,
  entry: GlossaryEntryUpdate
): Promise<GlossaryEntry> => {
  const { data } = await api.patch(
    `/novels/${novelId}/glossary/${entryId}`,
    entry
  );
  return data;
};

export const deleteGlossaryEntry = async (
  novelId: number,
  entryId: number
): Promise<void> => {
  await api.delete(`/novels/${novelId}/glossary/${entryId}`);
};
