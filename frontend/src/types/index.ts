export interface Novel {
  id: number;
  name: string;
  updated_on: string;
}

export interface NovelCreate {
  name: string;
}

export interface NovelUpdate {
  name?: string;
}

export type ChapterStatus =
  | "pending"
  | "analyzing"
  | "translating"
  | "completed"
  | "failed";

export interface Chapter {
  id: number;
  novel_id: number;
  number: number;
  source_text: string;
  translated_text: string | null;
  status: ChapterStatus;
  error: string | null;
  new_terms_count: number | null;
  updated_on: string;
}

export interface ChapterUpdate {
  number?: number;
  source_text?: string;
  translated_text?: string;
}

export interface GlossaryEntry {
  id: number;
  novel_id: number;
  source_term: string;
  translation: string;
}

export interface GlossaryEntryCreate {
  source_term: string;
  translation: string;
}

export interface GlossaryEntryUpdate {
  source_term?: string;
  translation?: string;
}
