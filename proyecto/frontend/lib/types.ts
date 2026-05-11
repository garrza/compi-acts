export type RawRow = {
  id: number;
  source_file: string;
  created_at: string;
};

export type CleanedRow = {
  id: number;
  source_file: string;
  created_at: string;
};

export type KeywordsRow = {
  id: number;
  source_file: string;
  keywords: string | null;
  created_at: string;
};

export type CategorizedRow = {
  id: number;
  source_file: string;
  keywords: string | null;
  category: string | null;
  created_at: string;
};

export type TableKey = "raw" | "cleaned" | "keywords" | "categories";

export const TABLE_LABELS: Record<TableKey, string> = {
  raw: "Raw data",
  cleaned: "Cleaned data",
  keywords: "Keywords",
  categories: "Categorized",
};

export const TABLE_DB_NAMES: Record<TableKey, string> = {
  raw: "raw_data",
  cleaned: "cleaned_data",
  keywords: "keywords_data",
  categories: "categorized_data",
};
