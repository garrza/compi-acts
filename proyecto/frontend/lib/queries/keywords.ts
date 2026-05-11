import "server-only";
import { db, safeQuery } from "@/lib/db";
import type { KeywordsRow } from "@/lib/types";

export function countKeywords(): number {
  return safeQuery(
    () =>
      (db()
        .prepare("SELECT COUNT(*) AS c FROM keywords_data")
        .get() as { c: number }).c,
    0,
  );
}

export function listKeywords(limit = 100): KeywordsRow[] {
  return safeQuery(
    () =>
      db()
        .prepare(
          "SELECT id, source_file, keywords, created_at FROM keywords_data ORDER BY id DESC LIMIT ?",
        )
        .all(limit) as KeywordsRow[],
    [],
  );
}
