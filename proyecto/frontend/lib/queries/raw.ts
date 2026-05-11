import "server-only";
import { db, safeQuery } from "@/lib/db";
import type { RawRow } from "@/lib/types";

export function countRaw(): number {
  return safeQuery(
    () =>
      (db()
        .prepare("SELECT COUNT(*) AS c FROM raw_data")
        .get() as { c: number }).c,
    0,
  );
}

export function listRaw(limit = 100): RawRow[] {
  return safeQuery(
    () =>
      db()
        .prepare(
          "SELECT id, source_file, created_at FROM raw_data ORDER BY id DESC LIMIT ?",
        )
        .all(limit) as RawRow[],
    [],
  );
}
