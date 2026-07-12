"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { publicEnv } from "@/config/env";
import { useAuth } from "@/lib/auth/auth-context";
import { isRole, landingForRole } from "@/lib/auth/session";

const loginSchema = z.object({
  email: z.email("Enter a valid email address."),
  password: z.string().min(1, "Password is required."),
  remember: z.boolean().optional(),
});

type LoginValues = z.infer<typeof loginSchema>;

// The typed client strips `/api/v1`; the login endpoint lives back under it.
const API_BASE = publicEnv.NEXT_PUBLIC_API_BASE_URL.replace(/\/api\/v1\/?$/, "");
const LOGIN_URL = `${API_BASE}/api/v1/auth/login`;

export function LoginForm() {
  const router = useRouter();
  const { login } = useAuth();
  const [authError, setAuthError] = useState<string | null>(null);

  const form = useForm<LoginValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
      remember: true,
    },
  });

  async function onSubmit(values: LoginValues) {
    setAuthError(null);
    try {
      const res = await fetch(LOGIN_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: values.email, password: values.password }),
      });

      if (res.status === 401) {
        setAuthError("Incorrect email or password.");
        return;
      }
      if (res.status === 423) {
        setAuthError("Account locked after 5 failed attempts. Try again later.");
        return;
      }
      if (!res.ok) {
        setAuthError("Something went wrong. Please try again.");
        return;
      }

      const data = (await res.json()) as {
        name: string;
        email: string;
        role: string;
      };
      if (!isRole(data.role)) {
        setAuthError("Your account role is not recognized. Contact an admin.");
        return;
      }

      login({ name: data.name, email: data.email, role: data.role });
      toast.success("Signed in", {
        description: `Welcome back, ${data.name}.`,
      });
      router.push(landingForRole(data.role));
    } catch {
      setAuthError("Unable to reach the server. Check your connection.");
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input
                  type="email"
                  placeholder="raven@transitops.in"
                  autoComplete="email"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Password</FormLabel>
              <FormControl>
                <Input
                  type="password"
                  placeholder="••••••••"
                  autoComplete="current-password"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {authError ? (
          <p
            role="alert"
            className="border-destructive/40 bg-destructive/10 text-destructive rounded-md border px-3 py-2 text-sm"
          >
            {authError}
          </p>
        ) : null}

        <div className="flex items-center justify-between">
          <FormField
            control={form.control}
            name="remember"
            render={({ field }) => (
              <FormItem className="flex flex-row items-center gap-2 space-y-0">
                <FormControl>
                  <Checkbox
                    checked={field.value}
                    onCheckedChange={field.onChange}
                    id="remember"
                  />
                </FormControl>
                <Label htmlFor="remember" className="font-normal">
                  Remember me
                </Label>
              </FormItem>
            )}
          />
          <Link
            href="#"
            className="text-brand text-sm font-medium hover:underline"
          >
            Forgot password?
          </Link>
        </div>

        <Button
          type="submit"
          className="w-full"
          disabled={form.formState.isSubmitting}
        >
          {form.formState.isSubmitting ? "Signing in…" : "Sign in"}
        </Button>
      </form>
    </Form>
  );
}
