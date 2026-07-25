import * as React from "react"
import { cn } from "@/utils/cn"

export interface PopoverProps {
  children: React.ReactNode
}

export function Popover({ children }: PopoverProps) {
  const [open, setOpen] = React.useState(false);
  const containerRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div ref={containerRef} className="relative inline-block text-left">
      {React.Children.map(children, child => {
        if (!React.isValidElement(child)) return child;
        if (child.type === PopoverTrigger) {
          return React.cloneElement(child as React.ReactElement<any>, {
            onClick: () => setOpen(!open),
            "aria-expanded": open
          });
        }
        if (child.type === PopoverContent) {
          if (!open) return null;
          return React.cloneElement(child as React.ReactElement<any>, {
            onClose: () => setOpen(false)
          });
        }
        return child;
      })}
    </div>
  );
}

export function PopoverTrigger({ children, onClick, ...props }: any) {
  return React.cloneElement(React.Children.only(children), {
    onClick,
    ...props
  });
}

export function PopoverContent({ className, align = "right", children, onClose, styled = false, ...props }: any) {
  return (
    <div
      className={cn(
        "absolute z-50 mt-2 outline-none animate-in fade-in-0 zoom-in-95",
        styled && "rounded-md border bg-popover text-popover-foreground shadow-md p-4",
        align === "right" ? "right-0 origin-top-right" : "left-0 origin-top-left",
        className
      )}
      {...props}
    >
      {React.Children.map(children, child => {
        if (React.isValidElement(child)) {
          return React.cloneElement(child as React.ReactElement<any>, {
            onClose
          });
        }
        return child;
      })}
    </div>
  )
}
