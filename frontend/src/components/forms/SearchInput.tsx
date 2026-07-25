import { Search, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface SearchInputProps {
  value: string;
  placeholder?: string;
  onChange: (value: string) => void;
}

export function SearchInput({ value, placeholder = "Search...", onChange }: SearchInputProps) {
  return (
    <div className="relative w-full sm:max-w-sm">
      <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
      <Input
        className="pl-9 pr-8"
        onChange={event => onChange(event.target.value)}
        placeholder={placeholder}
        value={value}
      />
      {value ? (
        <Button
          className="absolute right-1 top-1/2 -translate-y-1/2"
          onClick={() => onChange("")}
          size="sm"
          type="button"
          variant="ghost"
        >
          <X className="h-4 w-4" />
        </Button>
      ) : null}
    </div>
  );
}
