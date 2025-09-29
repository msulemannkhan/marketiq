"use client";

import type React from "react";
import { useState } from "react";
import { Lock, User } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { AuthInput } from "@/components/ui/AuthInput";
import { Checkbox, Spinner } from "@heroui/react";
import { BRAND_CONFIG } from "@/lib/config/brand-config";
import { AuthBranding } from "./AuthBranding";
import { useAuthForm } from "@/hooks/useAuthForm";
import { validateLoginForm } from "@/lib/utils/validation";

export function LoginForm() {
  const [showPassword, setShowPassword] = useState(false);
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);

  const { isSubmitting, error, fieldErrors, submitForm } = useAuthForm({
    validateForm: (data) => {
      if ('login' in data) {
        return validateLoginForm(data.login, data.password);
      }
      return {};
    }
  });

  const handleLogin = async () => {
    await submitForm({
      login,
      password,
      remember_me: rememberMe
    });
  };

  const togglePasswordVisibility = () => setShowPassword(!showPassword);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    void handleLogin();
  };

  return (
    <div className="w-full max-w-lg space-y-10">
      {/* Mobile Branding */}
      <AuthBranding variant="mobile" />

      <div className="space-y-8">
        <div className="space-y-4 text-center lg:text-left">
          <h2 className="text-5xl font-bold text-foreground tracking-tight">
            {BRAND_CONFIG.auth.login.title}
          </h2>
          <p className="text-xl text-muted-foreground font-light leading-relaxed">
            {BRAND_CONFIG.auth.login.subtitle}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8" autoComplete="off">
          {/* Hidden inputs to trick autofill */}
          <input type="text" style={{ display: "none" }} autoComplete="new-password" />
          <input type="password" style={{ display: "none" }} autoComplete="new-password" />

          {/* Login Field (Username or Email) */}
          <AuthInput
            id="login"
            name="login"
            label="Username or Email"
            type="text"
            value={login}
            onChange={(e) => setLogin(e.target.value)}
            placeholder="Enter your username or email"
            required
            icon={User}
            error={!!error || !!fieldErrors.login}
          />
          {fieldErrors.login && (
            <p className="text-sm text-red-600 mt-1">{fieldErrors.login}</p>
          )}

          {/* Password Field */}
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-lg font-semibold text-foreground">{BRAND_CONFIG.auth.login.fields.password.label}</span>
              <Link
                href="/forgot-password"
                className="text-lg text-primary hover:text-primary/80 font-medium transition-colors"
              >
                {BRAND_CONFIG.auth.login.actions.forgotPassword}
              </Link>
            </div>
            <AuthInput
              id="userPassword"
              name="userPassword"
              label=""
              placeholder={BRAND_CONFIG.auth.login.fields.password.placeholder}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="new-password"
              icon={Lock}
              showPasswordToggle
              showPassword={showPassword}
              onTogglePassword={togglePasswordVisibility}
              error={!!error || !!fieldErrors.password}
            />
            {fieldErrors.password && (
              <p className="text-sm text-red-600 mt-1">{fieldErrors.password}</p>
            )}
          </div>

          {/* Remember Me */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Checkbox
                size="md"
                isSelected={rememberMe}
                onValueChange={setRememberMe}
              >
                {BRAND_CONFIG.auth.login.actions.rememberMe}
              </Checkbox>
            </div>
          </div>

          {/* Error Message */}
          {error ? (
            <div
              className="text-sm text-red-600 bg-red-50 dark:bg-red-900/20 dark:text-red-400 p-4 rounded-lg border border-red-200 dark:border-red-800 flex items-center gap-2"
              role="alert"
              aria-live="polite"
            >
              <div className="w-2 h-2 bg-red-500 rounded-full flex-shrink-0" />
              {error}
            </div>
          ) : null}

          {/* Submit Button */}
          <Button
            type="submit"
            variant="default"
            disabled={isSubmitting || !login || !password}
            className="w-full h-16 rounded-xl bg-primary hover:bg-primary/90 disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-3 font-bold text-xl transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            {isSubmitting ? (
              <>
                <Spinner color="current" size="sm" />
                Signing in...
              </>
            ) : (
              BRAND_CONFIG.auth.login.actions.submit
            )}
          </Button>
        </form>

        {/* Sign Up Link */}
        <div className="text-center">
          <p className="text-muted-foreground text-lg font-light">
            {BRAND_CONFIG.auth.login.actions.noAccount}{" "}
            <Link
              href="/register"
              className="text-primary hover:text-primary/80 font-semibold transition-colors text-lg"
            >
              {BRAND_CONFIG.auth.login.actions.createAccount}
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}