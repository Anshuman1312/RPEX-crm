import { cn } from "@/utils/cn";

interface SkeletonBlockProps {
  className?: string;
}

export function SkeletonBlock({ className }: SkeletonBlockProps) {
  return <div className={cn("animate-pulse rounded-md bg-muted", className)} />;
}
