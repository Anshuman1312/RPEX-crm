import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { useLocation, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { appPaths } from "@/routes/config/paths";
import { tokenStorage } from "@/core/auth/tokenStorage";
import { useAppDispatch } from "@/hooks/redux";
import { useLoginMutation } from "@/features/auth/services/authApi";
import { setCredentials } from "@/features/auth/store/authSlice";
import { loginSchema, type LoginFormValues } from "@/features/auth/validation/authSchemas";

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useAppDispatch();
  const [login] = useLoginMutation();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting }
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "", rememberMe: true }
  });

  const onSubmit = async (values: LoginFormValues) => {
    try {
      const redirectTo =
        (location.state as { from?: { pathname?: string } } | null)?.from?.pathname ??
        appPaths.dashboard;

      const response = await login({
        email: values.email,
        password: values.password
      }).unwrap();

      tokenStorage.persistAuth({
        accessToken: response.accessToken,
        refreshToken: response.refreshToken,
        session: response.session,
        rememberMe: Boolean(values.rememberMe)
      });

      dispatch(
        setCredentials({
          accessToken: response.accessToken,
          refreshToken: response.refreshToken,
          session: response.session,
          rememberMe: Boolean(values.rememberMe)
        })
      );

      navigate(redirectTo, { replace: true });
    } catch {
      toast.error("Unable to sign in. Please verify your credentials and try again.");
    }
  };

  return (
    <Card className="min-h-[34rem] w-full max-w-md border shadow-lg">
      <CardHeader className="items-center text-center">
        <img
          src="/logo.png"
          alt="RPEX CRM logo"
          className="h-44 w-44 object-contain"
        />
        <CardTitle>Sign in to RPEX CRM</CardTitle>
      </CardHeader>
      <CardContent>
        <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
          <div className="space-y-1">
            <label className="text-sm font-medium" htmlFor="email">
              Email
            </label>
            <Input id="email" type="email" {...register("email")} />
            {errors.email && <p className="text-xs text-destructive">{errors.email.message}</p>}
          </div>

          <div className="space-y-1">
            <label className="text-sm font-medium" htmlFor="password">
              Password
            </label>
            <Input id="password" type="password" {...register("password")} />
            {errors.password && (
              <p className="text-xs text-destructive">{errors.password.message}</p>
            )}
          </div>

          <label className="flex items-center gap-2 text-sm text-muted-foreground">
            <input className="h-4 w-4" type="checkbox" {...register("rememberMe")} />
            Keep me signed in on this device
          </label>

          <Button className="w-full" disabled={isSubmitting} type="submit">
            {isSubmitting ? "Signing in..." : "Sign in"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
