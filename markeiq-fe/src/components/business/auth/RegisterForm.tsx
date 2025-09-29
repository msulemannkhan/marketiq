"use client";

import type React from "react";
import { useState } from "react";
import { Mail, Lock, User } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { AuthInput } from "@/components/ui/AuthInput";
import { Checkbox, Spinner } from "@heroui/react";
import { BRAND_CONFIG } from "@/lib/config/brand-config";
import { AuthBranding } from "./AuthBranding";
import { useAuthForm } from "@/hooks/useAuthForm";
import { validateRegisterForm } from "@/lib/utils/validation";

export function RegisterForm() {
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    full_name: "",
    username: "",
    email: "",
    password: "",
    confirmPassword: ""
  });
  const [acceptTerms, setAcceptTerms] = useState(false);

  const { isSubmitting, error, fieldErrors, submitForm } = useAuthForm({
    validateForm: (data) => {
      if ('full_name' in data) {
        return validateRegisterForm(
          data.full_name,
          data.username,
          data.email,
          data.password,
        );
      }
      return {};
    }
  });

  const handleRegister = async () => {
    if (!acceptTerms) {
      return;
    }

    await submitForm({
      full_name: formData.full_name,
      username: formData.username,
      email: formData.email,
      password: formData.password
    });
  };

  const togglePasswordVisibility = () => setShowPassword(!showPassword);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    void handleRegister();
  };

  const handleInputChange = (field: keyof typeof formData) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({ ...prev, [field]: e.target.value }));
  };

  const isFormValid = formData.full_name && formData.username && formData.email && formData.password && formData.confirmPassword && acceptTerms;

  return (
    <div className="w-full max-w-lg space-y-10">
      {/* Mobile Branding */}
      <AuthBranding variant="mobile" />

      <div className="space-y-8">
        <div className="space-y-4 text-center lg:text-left">
          <h2 className="text-5xl font-bold text-foreground tracking-tight">
            {BRAND_CONFIG.auth.register.title}
          </h2>
          <p className="text-xl text-muted-foreground font-light leading-relaxed">
            {BRAND_CONFIG.auth.register.subtitle}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8" autoComplete="off">
          {/* Hidden inputs to trick autofill */}
          <input type="text" style={{ display: "none" }} autoComplete="new-password" />
          <input type="password" style={{ display: "none" }} autoComplete="new-password" />

          {/* Full Name Field */}
          <AuthInput
            id="full_name"
            name="full_name"
            label="Full Name"
            type="text"
            value={formData.full_name}
            onChange={handleInputChange('full_name')}
            placeholder="Enter your full name"
            required
            icon={User}
            error={!!error || !!fieldErrors.full_name}
          />
          {fieldErrors.full_name && (
            <p className="text-sm text-red-600 mt-1">{fieldErrors.full_name}</p>
          )}

          {/* Username Field */}
          <AuthInput
            id="username"
            name="username"
            label={BRAND_CONFIG.auth.register.fields.username.label}
            type="text"
            value={formData.username}
            onChange={handleInputChange('username')}
            placeholder={BRAND_CONFIG.auth.register.fields.username.placeholder}
            required
            icon={User}
            error={!!error || !!fieldErrors.username}
          />
          {fieldErrors.username && (
            <p className="text-sm text-red-600 mt-1">{fieldErrors.username}</p>
          )}

          {/* Email Field */}
          <AuthInput
            id="email"
            name="email"
            label={BRAND_CONFIG.auth.register.fields.email.label}
            type="email"
            value={formData.email}
            onChange={handleInputChange('email')}
            placeholder={BRAND_CONFIG.auth.register.fields.email.placeholder}
            required
            icon={Mail}
            error={!!error || !!fieldErrors.email}
          />
          {fieldErrors.email && (
            <p className="text-sm text-red-600 mt-1">{fieldErrors.email}</p>
          )}

          {/* Password Field */}
          <AuthInput
            id="password"
            name="password"
            label="Password"
            placeholder="Enter your password"
            value={formData.password}
            onChange={handleInputChange('password')}
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

          {/* Confirm Password Field */}
          <AuthInput
            id="confirmPassword"
            name="confirmPassword"
            label="Confirm Password"
            placeholder="Confirm your password"
            value={formData.confirmPassword}
            onChange={handleInputChange('confirmPassword')}
            required
            autoComplete="new-password"
            icon={Lock}
            showPasswordToggle
            showPassword={showPassword}
            onTogglePassword={togglePasswordVisibility}
            error={!!error || !!fieldErrors.confirmPassword}
          />
          {fieldErrors.confirmPassword && (
            <p className="text-sm text-red-600 mt-1">{fieldErrors.confirmPassword}</p>
          )}

          {/* Terms & Conditions */}
          <div className="flex items-start space-x-3">
            <Checkbox
              isSelected={acceptTerms}
              onValueChange={setAcceptTerms}
              size="md"
              className="mt-1"
            >
              <span className="text-lg text-muted-foreground font-light leading-relaxed">
                I agree to the{" "}
                <Link href="/terms" className="text-primary hover:text-primary/80 font-medium transition-colors">
                  Terms & Conditions
                </Link>
                {" "}and{" "}
                <Link href="/privacy" className="text-primary hover:text-primary/80 font-medium transition-colors">
                  Privacy Policy
                </Link>
              </span>
            </Checkbox>
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
            disabled={isSubmitting || !isFormValid}
            className="w-full h-16 rounded-xl bg-primary hover:bg-primary/90 disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-3 font-bold text-xl transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            {isSubmitting ? (
              <>
                <Spinner color="current" size="sm" />
                Creating account...
              </>
            ) : (
              BRAND_CONFIG.auth.register.actions.submit
            )}
          </Button>
        </form>

        {/* Sign In Link */}
        <div className="text-center">
          <p className="text-muted-foreground text-lg font-light">
            Already have an account?{" "}
            <Link
              href="/login"
              className="text-primary hover:text-primary/80 font-semibold transition-colors text-lg"
            >
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}