import { LogOut, Settings, UserCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ProfileMenuProps {
  userName: string;
  userEmail: string;
  onSignOut: () => void;
}

export function ProfileMenu({ userName, userEmail, onSignOut }: ProfileMenuProps) {
  return (
    <div className="w-72 rounded-lg border bg-card p-3 shadow-lg">
      <div className="mb-3 flex items-center gap-2 border-b pb-3">
        <UserCircle2 className="h-8 w-8 text-primary" />
        <div>
          <p className="text-sm font-semibold">{userName}</p>
          <p className="text-xs text-muted-foreground">{userEmail}</p>
        </div>
      </div>

      <div className="space-y-2">
        <Button className="w-full justify-start" size="sm" variant="ghost">
          <UserCircle2 className="mr-2 h-4 w-4" />
          My Profile
        </Button>
        <Button className="w-full justify-start" size="sm" variant="ghost">
          <Settings className="mr-2 h-4 w-4" />
          Account Settings
        </Button>
        <Button className="w-full justify-start text-destructive hover:text-destructive" onClick={onSignOut} size="sm" variant="ghost">
          <LogOut className="mr-2 h-4 w-4" />
          Sign out
        </Button>
      </div>
    </div>
  );
}
