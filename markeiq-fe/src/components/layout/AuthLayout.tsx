import type React from "react";

interface AuthLayoutProps {
  leftSide: React.ReactNode;
  rightSide: React.ReactNode;
}

export function AuthLayout({ leftSide, rightSide }: AuthLayoutProps) {
  return (
    <div className="min-h-screen flex">
      {/* Left Side - Hero */}
      <div className="hidden lg:flex lg:w-1/2">
        {leftSide}
      </div>

      {/* Right Side - Form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-background">
        {rightSide}
      </div>
    </div>
  );
}