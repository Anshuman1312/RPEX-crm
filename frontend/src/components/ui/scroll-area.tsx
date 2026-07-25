import * as React from "react"
import { cn } from "@/utils/cn"

export interface ScrollAreaProps extends React.HTMLAttributes<HTMLDivElement> {
  viewportClassName?: string;
}

const ScrollArea = React.forwardRef<HTMLDivElement, ScrollAreaProps>(
  ({ className, children, viewportClassName, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn("relative overflow-hidden w-full h-full", className)}
        {...props}
      >
        <div
          className={cn(
            "h-full w-full overflow-y-auto custom-scrollbar",
            viewportClassName
          )}
        >
          {children}
        </div>
      </div>
    )
  }
)
ScrollArea.displayName = "ScrollArea"

const ScrollBar = () => null

export { ScrollArea, ScrollBar }
