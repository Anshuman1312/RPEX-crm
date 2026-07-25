import { useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { useSelector } from "react-redux";
import { toast } from "sonner";
import { Button, FormField, Input } from "@/components";
import { PageContainer } from "@/layouts/components/PageContainer";
import { RootState } from "@/app/store";
import { ProfileFormValues, profileSchema } from "@/features/profile/validation/profileSchemas";

function getInitials(name: string): string {
  return name
    .split(" ")
    .map(part => part[0]?.toUpperCase() ?? "")
    .slice(0, 2)
    .join("");
}

export function ProfilePage() {
  const session = useSelector((state: RootState) => state.auth.session);
  const [isEditing, setIsEditing] = useState(false);
  const [saved, setSaved] = useState<ProfileFormValues>({
    displayName: session?.name ?? "",
    phone: "",
    city: "",
    bio: ""
  });

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isDirty }
  } = useForm<ProfileFormValues>({
    resolver: zodResolver(profileSchema),
    defaultValues: saved
  });

  const handleEdit = () => {
    reset(saved);
    setIsEditing(true);
  };

  const handleCancel = () => {
    reset(saved);
    setIsEditing(false);
  };

  const handleSave = (values: ProfileFormValues) => {
    setSaved(values);
    setIsEditing(false);
    toast.success("Profile updated successfully");
  };

  const initials = getInitials(saved.displayName || session?.name || "U");

  return (
    <PageContainer
      actions={
        !isEditing ? (
          <Button onClick={handleEdit} variant="outline">
            Edit Profile
          </Button>
        ) : undefined
      }
      description="Manage your personal information, contact details, and account overview."
      title="My Profile"
    >
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Avatar + identity card */}
        <div className="flex flex-col items-center gap-4 rounded-lg border bg-card p-6 text-center lg:col-span-1">
          <div className="flex h-20 w-20 items-center justify-center rounded-full bg-primary text-2xl font-bold text-primary-foreground">
            {initials}
          </div>
          <div>
            <p className="text-lg font-semibold">{saved.displayName || session?.name}</p>
            <p className="text-sm text-muted-foreground">{session?.email}</p>
          </div>
          <span className="rounded-full bg-muted px-3 py-1 text-xs font-medium">
            {session?.role?.replace(/_/g, " ")}
          </span>
          {saved.city ? (
            <p className="text-xs text-muted-foreground">{saved.city}</p>
          ) : null}
          {saved.bio ? (
            <p className="max-w-xs text-sm text-muted-foreground">{saved.bio}</p>
          ) : null}
        </div>

        {/* Details panel */}
        <div className="space-y-6 lg:col-span-2">
          {/* Read-only session info */}
          <section className="rounded-lg border bg-card p-5 space-y-4">
            <h3 className="text-sm font-semibold">Account Information</h3>
            <dl className="grid gap-3 text-sm sm:grid-cols-2">
              <InfoRow label="User ID" value={session?.userId ?? "—"} />
              <InfoRow label="Email" value={session?.email ?? "—"} />
              <InfoRow label="Role" value={session?.role?.replace(/_/g, " ") ?? "—"} />
              <InfoRow
                label="Permissions"
                value={`${session?.permissions?.length ?? 0} granted`}
              />
            </dl>
          </section>

          {/* Editable details */}
          <section className="rounded-lg border bg-card p-5 space-y-4">
            <h3 className="text-sm font-semibold">Personal Details</h3>
            {isEditing ? (
              <form className="grid gap-3 sm:grid-cols-2" onSubmit={handleSubmit(handleSave)}>
                <FormField
                  error={errors.displayName?.message}
                  id="profile-display-name"
                  label="Display Name"
                  required
                >
                  <Input id="profile-display-name" {...register("displayName")} />
                </FormField>

                <FormField error={errors.phone?.message} id="profile-phone" label="Phone">
                  <Input id="profile-phone" {...register("phone")} />
                </FormField>

                <FormField error={errors.city?.message} id="profile-city" label="City">
                  <Input id="profile-city" {...register("city")} />
                </FormField>

                <div className="col-span-full">
                  <FormField error={errors.bio?.message} id="profile-bio" label="Bio">
                    <Input id="profile-bio" {...register("bio")} />
                  </FormField>
                </div>

                <div className="col-span-full flex justify-end gap-2">
                  <Button onClick={handleCancel} type="button" variant="outline">
                    Cancel
                  </Button>
                  <Button disabled={!isDirty} type="submit">
                    Save Changes
                  </Button>
                </div>
              </form>
            ) : (
              <dl className="grid gap-3 text-sm sm:grid-cols-2">
                <InfoRow label="Display Name" value={saved.displayName || "—"} />
                <InfoRow label="Phone" value={saved.phone || "—"} />
                <InfoRow label="City" value={saved.city || "—"} />
                <InfoRow label="Bio" value={saved.bio || "—"} />
              </dl>
            )}
          </section>
        </div>
      </div>
    </PageContainer>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs text-muted-foreground">{label}</dt>
      <dd className="font-medium">{value}</dd>
    </div>
  );
}
