import type { ReactNode, TdHTMLAttributes, ThHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

export function Thead({ children }: { children: ReactNode }) {
  return (
    <thead>
      <tr className="bg-hairline text-left">{children}</tr>
    </thead>
  );
}

export function Th({
  children,
  className,
  ...props
}: ThHTMLAttributes<HTMLTableCellElement>) {
  return (
    <th
      className={cn(
        "border-b border-border px-2.5 py-1.5 text-[10px] font-medium uppercase tracking-wider text-muted",
        className,
      )}
      {...props}
    >
      {children}
    </th>
  );
}

export function Tr({
  children,
  highlight = false,
  className,
  ...props
}: {
  children: ReactNode;
  highlight?: boolean;
  className?: string;
} & React.HTMLAttributes<HTMLTableRowElement>) {
  return (
    <tr
      className={cn(
        "border-b border-hairline last:border-0 hover:bg-hairline/60",
        highlight && "bg-primary-soft",
        className,
      )}
      {...props}
    >
      {children}
    </tr>
  );
}

export function Td({
  children,
  className,
  ...props
}: TdHTMLAttributes<HTMLTableCellElement>) {
  return (
    <td className={cn("px-2.5 py-[5px] text-xs text-fg", className)} {...props}>
      {children}
    </td>
  );
}
