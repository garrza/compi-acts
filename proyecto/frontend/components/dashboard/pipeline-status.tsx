import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import type { TableCounts } from "@/lib/queries/stats";
import type { TableKey } from "@/lib/types";
import { TABLE_LABELS } from "@/lib/types";

const ORDER: TableKey[] = ["raw", "cleaned", "keywords", "categories"];

export function PipelineStatus({ counts }: { counts: TableCounts }) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      {ORDER.map((step, i) => {
        const done = counts[step] > 0;
        return (
          <div key={step} className="flex items-center gap-2">
            <Badge variant={done ? "default" : "secondary"}>
              {i + 1}. {TABLE_LABELS[step]} ·{" "}
              <span className="ml-1 tabular-nums">{counts[step]}</span>
            </Badge>
            {i < ORDER.length - 1 ? (
              <Separator orientation="vertical" className="h-4" />
            ) : null}
          </div>
        );
      })}
    </div>
  );
}
