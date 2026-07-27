import { Building2 } from "lucide-react";
import { Outlet } from "react-router-dom";

export function AuthLayout() {
  return (
    <div className="grid min-h-screen bg-background lg:grid-cols-[1.1fr_1fr]">
      <aside className="relative hidden overflow-hidden border-r bg-muted lg:block">
        <img
          src="/image-2.jpeg"
          alt="Illustration"
          className="absolute inset-0 h-full w-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/30 to-black/50 z-10" />
        
        <div className="relative z-20 flex h-full flex-col justify-between p-12 text-white">
          <div className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-black/40 px-3 py-1 text-xs font-medium text-white/90 backdrop-blur self-start">
            <Building2 className="h-3.5 w-3.5 text-primary-foreground" />
            Enterprise CRM Platform
          </div>
        </div>
      </aside>

      <main className="grid place-items-center p-6 lg:p-10">
        <div className="w-full max-w-md">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
