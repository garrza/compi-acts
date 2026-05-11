import "server-only";
import { db, safeQuery } from "@/lib/db";
import type { CleanedRow } from "@/lib/types";

export function countCleaned(): number {
  return safeQuery(
    () =>
      (db()
        .prepare("SELECT COUNT(*) AS c FROM cleaned_data")
        .get() as { c: number }).c,
    0,
  );
}

export function listCleaned(limit = 100): CleanedRow[] {
  return safeQuery(
    () =>
      db()
        .prepare(
          "SELECT id, source_file, created_at FROM cleaned_data ORDER BY id DESC LIMIT ?",
        )
        .all(limit) as CleanedRow[],
    [],
  );
}
