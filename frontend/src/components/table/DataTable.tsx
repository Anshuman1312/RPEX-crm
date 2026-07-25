import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  SortingState,
  useReactTable,
  VisibilityState
} from "@tanstack/react-table";
import { useMemo, useState } from "react";
import { ArrowUpDown, ChevronDown } from "lucide-react";
import { cn } from "@/utils/cn";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { EmptyState } from "@/components/feedback";

interface DataTableProps<TData> {
  title: string;
  data: TData[];
  columns: ColumnDef<TData>[];
  globalSearchPlaceholder?: string;
  compact?: boolean;
}

export function DataTable<TData>({
  title,
  data,
  columns,
  globalSearchPlaceholder = "Search records...",
  compact = false
}: DataTableProps<TData>) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [globalFilter, setGlobalFilter] = useState("");
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({});
  const [rowSelection, setRowSelection] = useState({});
  const [showColumnsMenu, setShowColumnsMenu] = useState(false);

  const table = useReactTable({
    data,
    columns,
    state: {
      sorting,
      globalFilter,
      columnVisibility,
      rowSelection
    },
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    onColumnVisibilityChange: setColumnVisibility,
    onRowSelectionChange: setRowSelection,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel()
  });

  const visibleColumns = useMemo(() => table.getAllLeafColumns(), [table]);

  const exportCsv = () => {
    const rows = table.getFilteredRowModel().rows;
    const headers = table
      .getVisibleLeafColumns()
      .map((col) => String(col.columnDef.header ?? col.id));

    const lines = [headers.join(",")];

    rows.forEach((row) => {
      const line = row
        .getVisibleCells()
        .map((cell) => {
          const value = cell.getValue();
          const normalized =
            typeof value === "string" || typeof value === "number" ? String(value) : "";
          return `"${normalized.replace(/"/g, '""')}"`;
        })
        .join(",");
      lines.push(line);
    });

    const blob = new Blob([lines.join("\n")], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `${title.toLowerCase().replace(/\s+/g, "-")}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  };

  return (
    <section className="rounded-lg border bg-card p-4">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-sm font-semibold">{title}</h3>
        <div className="flex flex-wrap items-center gap-2">
          <Input
            className="h-9 w-56"
            onChange={(event) => setGlobalFilter(event.target.value)}
            placeholder={globalSearchPlaceholder}
            value={globalFilter}
          />
          <Button onClick={exportCsv} size="sm" variant="outline">
            Export CSV
          </Button>
          <div className="relative">
            <Button
              onClick={() => setShowColumnsMenu((value) => !value)}
              size="sm"
              variant="outline"
            >
              Columns
              <ChevronDown className="ml-2 h-4 w-4" />
            </Button>
            {showColumnsMenu ? (
              <div className="absolute right-0 z-10 mt-1 min-w-40 rounded-md border bg-card p-2 shadow-lg">
                {visibleColumns.map((column) => (
                  <label className="mb-1 flex items-center gap-2 text-xs" key={column.id}>
                    <input
                      checked={column.getIsVisible()}
                      onChange={column.getToggleVisibilityHandler()}
                      type="checkbox"
                    />
                    {String(column.columnDef.header ?? column.id)}
                  </label>
                ))}
              </div>
            ) : null}
          </div>
        </div>
      </div>

      <div className="overflow-x-auto rounded-md border custom-scrollbar">
        <table className={cn("w-full border-collapse", compact ? "text-xs" : "text-sm")}>
          <thead className="bg-muted/40">
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th
                    className={cn(
                      "border-b text-left font-semibold whitespace-nowrap",
                      compact ? "px-2.5 py-1.5" : "px-4 py-3"
                    )}
                    key={header.id}
                  >
                    {header.isPlaceholder ? null : (
                      <button
                        className="inline-flex items-center gap-1"
                        onClick={header.column.getToggleSortingHandler()}
                        type="button"
                      >
                        {flexRender(header.column.columnDef.header, header.getContext())}
                        <ArrowUpDown className={cn("text-muted-foreground", compact ? "h-3 w-3" : "h-3.5 w-3.5")} />
                      </button>
                    )}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.length > 0 ? (
              table.getRowModel().rows.map((row) => (
                <tr className="hover:bg-muted/20" key={row.id}>
                  {row.getVisibleCells().map((cell) => (
                    <td
                      className={cn(
                        "border-b whitespace-nowrap text-muted-foreground",
                        compact ? "px-2.5 py-1.5" : "px-4 py-3"
                      )}
                      key={cell.id}
                    >
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}
                </tr>
              ))
            ) : (
              <tr>
                <td className="p-3" colSpan={columns.length}>
                  <EmptyState
                    description="Try adjusting the search or filters."
                    title="No records found"
                  />
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="mt-4 flex items-center justify-between">
        <p className="text-xs text-muted-foreground">
          Selected {table.getSelectedRowModel().rows.length} of{" "}
          {table.getFilteredRowModel().rows.length}
        </p>
        <div className="flex items-center gap-2">
          <Button
            disabled={!table.getCanPreviousPage()}
            onClick={() => table.previousPage()}
            size="sm"
            variant="outline"
          >
            Previous
          </Button>
          <span className="text-xs text-muted-foreground">
            Page {table.getState().pagination.pageIndex + 1} of {table.getPageCount()}
          </span>
          <Button
            disabled={!table.getCanNextPage()}
            onClick={() => table.nextPage()}
            size="sm"
            variant="outline"
          >
            Next
          </Button>
        </div>
      </div>
    </section>
  );
}
