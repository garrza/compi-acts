import "server-only";
import { db, safeQuery } from "@/lib/db";
import type { CategorizedRow } from "@/lib/types";

export function countCategorized(): number {
  return safeQuery(
    () =>
      (db()
        .prepare("SELECT COUNT(*) AS c FROM categorized_data")
        .get() as { c: number }).c,
    0,
  );
}

export function listCategorized(limit = 100): CategorizedRow[] {
  return safeQuery(
    () =>
      db()
        .prepare(
          "SELECT id, source_file, keywords, category, created_at FROM categorized_data ORDER BY id DESC LIMIT ?",
        )
        .all(limit) as CategorizedRow[],
    [],
  );
}

export type CategoryBucket = { category: string; count: number };

export function categoryDistribution(): CategoryBucket[] {
  return safeQuery(
    () =>
      db()
        .prepare(
          `SELECT COALESCE(category, '(uncategorized)') AS category, COUNT(*) AS count
           FROM categorized_data
           GROUP BY category
           ORDER BY count DESC`,
        )
        .all() as CategoryBucket[],
    [],
  );
}
