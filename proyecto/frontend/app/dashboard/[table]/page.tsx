import { notFound } from "next/navigation";
import { Header } from "@/components/layout/header";
import { DataTable } from "@/components/dashboard/data-table";
import { TABLE_LABELS, type TableKey } from "@/lib/types";
import { listRaw } from "@/lib/queries/raw";
import { listCleaned } from "@/lib/queries/cleaned";
import { listKeywords } from "@/lib/queries/keywords";
import { listCategorized } from "@/lib/queries/categories";

const VALID: ReadonlySet<TableKey> = new Set([
  "raw",
  "cleaned",
  "keywords",
  "categories",
]);

export default async function TablePage({
  params,
}: {
  params: Promise<{ table: string }>;
}) {
  const { table } = await params;
  if (!VALID.has(table as TableKey)) notFound();
  const key = table as TableKey;

  return (
    <>
      <Header
        title={TABLE_LABELS[key]}
        description={`Last 100 rows from ${dbName(key)}.`}
      />
      <main className="flex flex-col gap-4 p-6">{renderTable(key)}</main>
    </>
  );
}

function dbName(key: TableKey): string {
  return {
    raw: "raw_data",
    cleaned: "cleaned_data",
    keywords: "keywords_data",
    categories: "categorized_data",
  }[key];
}

function renderTable(key: TableKey) {
  switch (key) {
    case "raw":
      return (
        <DataTable
          rows={listRaw()}
          columns={[
            { key: "id", label: "ID", className: "w-16 tabular-nums" },
            { key: "source_file", label: "Source file" },
            { key: "created_at", label: "Created at", className: "tabular-nums" },
          ]}
        />
      );
    case "cleaned":
      return (
        <DataTable
          rows={listCleaned()}
          columns={[
            { key: "id", label: "ID", className: "w-16 tabular-nums" },
            { key: "source_file", label: "Source file" },
            { key: "created_at", label: "Created at", className: "tabular-nums" },
          ]}
        />
      );
    case "keywords":
      return (
        <DataTable
          rows={listKeywords()}
          columns={[
            { key: "id", label: "ID", className: "w-16 tabular-nums" },
            { key: "source_file", label: "Source file" },
            { key: "keywords", label: "Keywords" },
            { key: "created_at", label: "Created at", className: "tabular-nums" },
          ]}
        />
      );
    case "categories":
      return (
        <DataTable
          rows={listCategorized()}
          columns={[
            { key: "id", label: "ID", className: "w-16 tabular-nums" },
            { key: "source_file", label: "Source file" },
            { key: "keywords", label: "Keywords" },
            { key: "category", label: "Category" },
            { key: "created_at", label: "Created at", className: "tabular-nums" },
          ]}
        />
      );
  }
}
