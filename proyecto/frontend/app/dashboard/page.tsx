import { Header } from "@/components/layout/header";
import { StatCard } from "@/components/dashboard/stat-card";
import { PipelineStatus } from "@/components/dashboard/pipeline-status";
import { CategoryPie } from "@/components/charts/category-pie";
import { PipelineBar } from "@/components/charts/pipeline-bar";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { tableCounts } from "@/lib/queries/stats";
import { categoryDistribution } from "@/lib/queries/categories";
import type { TableKey } from "@/lib/types";

const TABLE_KEYS: TableKey[] = ["raw", "cleaned", "keywords", "categories"];

export default async function DashboardPage() {
  const counts = tableCounts();
  const distribution = categoryDistribution();

  return (
    <>
      <Header
        title="Overview"
        description="Snapshot of the pipeline tables in data/app.db."
      />
      <main className="flex flex-col gap-6 p-6">
        <PipelineStatus counts={counts} />

        <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {TABLE_KEYS.map((key) => (
            <StatCard key={key} table={key} count={counts[key]} />
          ))}
        </section>

        <section className="grid gap-4 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Rows per pipeline stage</CardTitle>
            </CardHeader>
            <CardContent>
              <PipelineBar counts={counts} />
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Category distribution</CardTitle>
            </CardHeader>
            <CardContent>
              <CategoryPie data={distribution} />
            </CardContent>
          </Card>
        </section>
      </main>
    </>
  );
}
