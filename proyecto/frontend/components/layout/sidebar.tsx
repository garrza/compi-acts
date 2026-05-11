import Link from "next/link";
import { cn } from "@/lib/utils";
import { TABLE_LABELS, type TableKey } from "@/lib/types";

const TABLE_KEYS: TableKey[] = ["raw", "cleaned", "keywords", "categories"];

export function Sidebar() {
  return (
    <aside className="hidden w-56 shrink-0 border-r bg-sidebar text-sidebar-foreground md:flex md:flex-col">
      <div className="flex h-14 items-center px-4 font-heading text-base font-semibold">
        Compi · Acts
      </div>
      <nav className="flex flex-col gap-1 p-2 text-sm">
        <SidebarLink href="/dashboard" label="Overview" />
        <div className="mt-3 px-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
          Tables
        </div>
        {TABLE_KEYS.map((key) => (
          <SidebarLink
            key={key}
            href={`/dashboard/${key}`}
            label={TABLE_LABELS[key]}
          />
        ))}
      </nav>
    </aside>
  );
}

function SidebarLink({ href, label }: { href: string; label: string }) {
  return (
    <Link
      href={href}
      className={cn(
        "rounded-md px-3 py-2 text-sm transition-colors",
        "hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
      )}
    >
      {label}
    </Link>
  );
}
