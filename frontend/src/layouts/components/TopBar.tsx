import { Bell, Menu, Search, UserCircle2 } from "lucide-react";
import { Button, Popover, PopoverContent, PopoverTrigger } from "@/components";
import { ThemeModeSwitcher } from "@/layouts/components/ThemeModeSwitcher";
import { NotificationPanel } from "@/layouts/components/NotificationPanel";
import { ProfileMenu } from "@/layouts/components/ProfileMenu";
import { ShellSearchScope } from "@/layouts/types";
import { ThemeMode } from "@/store/uiSlice";

interface TopBarProps {
  themeMode: ThemeMode;
  resolvedTheme: "light" | "dark";
  unreadNotifications: number;
  searchScopes: ShellSearchScope[];
  onCycleThemeMode: () => void;
  onOpenMobileNav: () => void;
  userEmail: string;
  userName: string;
  onSignOut: () => void;
}

export function TopBar({
  themeMode,
  resolvedTheme,
  unreadNotifications,
  searchScopes,
  onCycleThemeMode,
  onOpenMobileNav,
  userEmail,
  userName,
  onSignOut
}: TopBarProps) {
  return (
    <header className="sticky top-0 z-10 border-b bg-background/95 backdrop-blur">
      <div className="flex h-16 items-center justify-between gap-3 px-4 lg:px-6">
        <div className="flex items-center gap-2 lg:hidden">
          <Button variant="outline" size="sm" onClick={onOpenMobileNav}>
            <Menu className="h-4 w-4" />
          </Button>
        </div>

        <div className="relative w-full max-w-xl">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            aria-label="Global search"
            className="h-10 w-full rounded-md border bg-card pl-9 pr-36 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            placeholder="Quick search leads, customers, projects..."
          />
          <select aria-label="Search scope" className="absolute right-1 top-1/2 h-8 -translate-y-1/2 rounded-md border bg-background px-2 text-xs">
            {searchScopes.map(scope => (
              <option key={scope.id} value={scope.id}>
                {scope.label}
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-2">
          <ThemeModeSwitcher mode={themeMode} onCycleMode={onCycleThemeMode} resolvedMode={resolvedTheme} />
          
          <Popover>
            <PopoverTrigger>
              <Button aria-label="Open notifications" variant="outline" size="sm" className="relative">
                <Bell className="h-4 w-4" />
                {unreadNotifications > 0 && (
                  <span className="absolute -right-1 -top-1 inline-flex h-4 min-w-4 items-center justify-center rounded-full bg-primary px-1 text-[10px] font-semibold text-primary-foreground">
                    {unreadNotifications}
                  </span>
                )}
              </Button>
            </PopoverTrigger>
            <PopoverContent align="right">
              <NotificationPanel unreadCount={unreadNotifications} />
            </PopoverContent>
          </Popover>

          <Popover>
            <PopoverTrigger>
              <Button aria-label="Open profile menu" variant="outline" size="sm">
                <UserCircle2 className="h-4 w-4" />
              </Button>
            </PopoverTrigger>
            <PopoverContent align="right">
              <ProfileMenu
                userEmail={userEmail}
                userName={userName}
                onSignOut={onSignOut}
              />
            </PopoverContent>
          </Popover>
        </div>
      </div>
    </header>
  );
}
