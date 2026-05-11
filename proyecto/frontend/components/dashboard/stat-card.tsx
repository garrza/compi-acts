import Link from "next/link";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { TableKey } from "@/lib/types";
import { TABLE_LABELS } from "@/lib/types";

type Props = {
  table: TableKey;
  count: number;
  description?: string;
};

export function StatCard({ table, count, description }: Props) {
  return (
    <Link href={`/dashboard/${table}`} className="block">
      <Card className="transition-colors hover:bg-muted/40">
        <CardHeader>
          <CardDescription>{TABLE_LABELS[table]}</CardDescription>
          <CardTitle className="text-3xl font-semibold tabular-nums">
            {count.toLocaleString()}
          </CardTitle>
        </CardHeader>
        {description ? (
          <CardContent className="text-xs text-muted-foreground">
            {description}
          </CardContent>
        ) : null}
      </Card>
    </Link>
  );
}
