import "server-only";
import { countRaw } from "@/lib/queries/raw";
import { countCleaned } from "@/lib/queries/cleaned";
import { countKeywords } from "@/lib/queries/keywords";
import { countCategorized } from "@/lib/queries/categories";
import type { TableKey } from "@/lib/types";

export type TableCounts = Record<TableKey, number>;

export function tableCounts(): TableCounts {
  return {
    raw: countRaw(),
    cleaned: countCleaned(),
    keywords: countKeywords(),
    categories: countCategorized(),
  };
}
