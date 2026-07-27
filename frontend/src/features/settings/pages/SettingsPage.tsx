import { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { Button } from "@/components";
import { THEME_MODE_LABELS, THEME_MODES } from "@/core/theme/theme.constants";
import { PageContainer } from "@/layouts/components/PageContainer";
import { RootState } from "@/app/store";
import { ThemeMode, setThemeMode } from "@/store/uiSlice";

type SettingsTab = "appearance" | "account" | "notifications";

const TABS: { id: SettingsTab; label: string }[] = [
  { id: "appearance", label: "Appearance" },
  { id: "account", label: "Account" },
  { id: "notifications", label: "Notifications" }
];

export function SettingsPage() {
  const [activeTab, setActiveTab] = useState<SettingsTab>("appearance");
  const dispatch = useDispatch();
  const themeMode = useSelector((state: RootState) => state.ui.themeMode);
  const resolvedTheme = useSelector((state: RootState) => state.ui.resolvedTheme);
  const session = useSelector((state: RootState) => state.auth.session);

  return (
    <PageContainer
      description="Manage your appearance, account details, and notification preferences."
      title="Settings"
    >
      {/* Tab Bar */}
      <nav className="flex border-b">
        {TABS.map(tab => (
          <button
            className={[
              "px-4 py-2 text-sm font-medium transition-colors",
              activeTab === tab.id
                ? "border-b-2 border-primary text-primary"
                : "text-muted-foreground hover:text-foreground"
            ].join(" ")}
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            type="button"
          >
            {tab.label}
          </button>
        ))}
      </nav>

      {/* Appearance */}
      {activeTab === "appearance" ? (
        <section className="space-y-6">
          <SettingsCard
            description="Choose how the interface looks. System follows your operating-system preference."
            title="Theme Mode"
          >
            <div className="flex flex-wrap gap-2">
              {THEME_MODES.map(mode => (
                <Button
                  key={mode}
                  onClick={() => dispatch(setThemeMode(mode as ThemeMode))}
                  variant={themeMode === mode ? "default" : "outline"}
                >
                  {THEME_MODE_LABELS[mode]}
                </Button>
              ))}
            </div>
            <p className="mt-2 text-xs text-muted-foreground">
              Current resolved theme: <strong>{resolvedTheme}</strong>
            </p>
          </SettingsCard>

          <SettingsCard
            description="Density and sidebar behaviour are managed automatically based on screen size."
            title="Layout"
          >
            <p className="text-sm text-muted-foreground">
              Sidebar collapses automatically on screens narrower than 1024 px. Use the toggle in the
              top-bar to override manually.
            </p>
          </SettingsCard>
        </section>
      ) : null}

      {/* Account */}
      {activeTab === "account" ? (
        <section className="space-y-6">
          <SettingsCard
            description="Current session details pulled from the authenticated token."
            title="Active Session"
          >
            {session ? (
              <dl className="grid gap-2 text-sm sm:grid-cols-2">
                <SettingsRow label="Email" value={session.email} />
                <SettingsRow label="Full Name" value={session.name ?? "—"} />
                <SettingsRow label="Role" value={session.role ?? "—"} />
                <SettingsRow label="User ID" value={session.userId} />
              </dl>
            ) : (
              <p className="text-sm text-muted-foreground">No active session data available.</p>
            )}
          </SettingsCard>

          <SettingsCard
            description="Password and credential changes are managed through the authentication service."
            title="Credentials"
          >
            <p className="text-sm text-muted-foreground">
              To update your password, use the Reset Password link on the login page. SSO credential
              changes are handled by your identity provider.
            </p>
          </SettingsCard>
        </section>
      ) : null}

      {/* Notifications */}
      {activeTab === "notifications" ? (
        <section className="space-y-6">
          <SettingsCard
            description="Control which events surface as in-app notifications."
            title="In-App Notifications"
          >
            <div className="space-y-3 text-sm">
              <NotificationToggleRow label="Booking stage changes" defaultChecked />
              <NotificationToggleRow label="Payment status updates" defaultChecked />
              <NotificationToggleRow label="Task assignments" defaultChecked />
              <NotificationToggleRow label="Approval requests" defaultChecked />
              <NotificationToggleRow label="System maintenance alerts" />
              <NotificationToggleRow label="Report generation completions" />
            </div>
          </SettingsCard>

          <SettingsCard
            description="Email delivery settings are managed by the backend notification service."
            title="Email Notifications"
          >
            <p className="text-sm text-muted-foreground">
              Email delivery preferences are configured at the organisation level. Contact your admin to
              adjust email digest frequency.
            </p>
          </SettingsCard>
        </section>
      ) : null}

    </PageContainer>
  );
}

/* ── Internal layout primitives ─────────────────────────────────────────── */

function SettingsCard({
  title,
  description,
  children
}: {
  title: string;
  description?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-lg border bg-card p-5 space-y-3">
      <div>
        <h3 className="text-sm font-semibold">{title}</h3>
        {description ? (
          <p className="mt-0.5 text-xs text-muted-foreground">{description}</p>
        ) : null}
      </div>
      {children}
    </div>
  );
}

function SettingsRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs text-muted-foreground">{label}</dt>
      <dd className="font-medium">{value}</dd>
    </div>
  );
}

function NotificationToggleRow({
  label,
  defaultChecked = false
}: {
  label: string;
  defaultChecked?: boolean;
}) {
  const [enabled, setEnabled] = useState(defaultChecked);

  return (
    <label className="flex cursor-pointer items-center justify-between gap-4">
      <span>{label}</span>
      <button
        aria-checked={enabled}
        className={[
          "relative inline-flex h-5 w-9 shrink-0 rounded-full border-2 border-transparent transition-colors focus-visible:outline-none",
          enabled ? "bg-primary" : "bg-muted"
        ].join(" ")}
        onClick={() => setEnabled(prev => !prev)}
        role="switch"
        type="button"
      >
        <span
          className={[
            "pointer-events-none inline-block h-4 w-4 rounded-full bg-white shadow transition-transform",
            enabled ? "translate-x-4" : "translate-x-0"
          ].join(" ")}
        />
      </button>
    </label>
  );
}
