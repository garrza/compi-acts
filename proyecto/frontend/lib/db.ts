import "server-only";
import path from "node:path";
import Database from "better-sqlite3";

const DB_PATH =
  process.env.APP_DB_PATH ??
  path.join(process.cwd(), "..", "data", "app.db");

let _db: Database.Database | null = null;

export function db(): Database.Database {
  if (!_db) {
    _db = new Database(DB_PATH, { readonly: true, fileMustExist: false });
  }
  return _db;
}

export function isMissingTableError(err: unknown): boolean {
  return (
    err instanceof Error &&
    /no such table/i.test(err.message)
  );
}

export function safeQuery<T>(fn: () => T, fallback: T): T {
  try {
    return fn();
  } catch (err) {
    if (isMissingTableError(err)) return fallback;
    throw err;
  }
}
