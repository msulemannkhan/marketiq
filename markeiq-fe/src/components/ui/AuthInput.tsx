import React from "react";
import { Eye, EyeOff, LucideIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface AuthInputProps {
  id: string;
  name: string;
  label: string;
  type?: "text" | "email" | "password";
  placeholder: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  required?: boolean;
  autoComplete?: string;
  error?: boolean;
  icon: LucideIcon;
  showPasswordToggle?: boolean;
  showPassword?: boolean;
  onTogglePassword?: () => void;
}

export function AuthInput({
  id,
  name,
  label,
  type = "text",
  placeholder,
  value,
  onChange,
  required = false,
  autoComplete = "off",
  error = false,
  icon: IconComponent,
  showPasswordToggle = false,
  showPassword = false,
  onTogglePassword,
}: AuthInputProps) {
  const inputType = showPasswordToggle ? (showPassword ? "text" : "password") : type;

  return (
    <div className="space-y-4">
      <Label htmlFor={id} className="text-lg font-semibold text-foreground">
        {label}
      </Label>
      <div className="relative">
        <Input
          id={id}
          name={name}
          type={inputType}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          required={required}
          autoComplete={autoComplete}
          className={`h-16 rounded-xl bg-background border-2 text-foreground pl-12 ${
            showPasswordToggle ? "pr-14" : ""
          } font-semibold transition-all duration-200 focus:ring-2 focus:ring-primary/20 placeholder:text-xl placeholder:font-normal ${
            error
              ? "border-red-500 focus:border-red-500 focus:ring-red-500/20"
              : "border-border focus:border-primary hover:border-primary/50"
          }`}
          style={{ 
            fontSize: '20px', 
            fontWeight: '500',
            // Prevent browser extensions from modifying these styles
            backgroundImage: 'none',
            backgroundRepeat: 'no-repeat',
            backgroundSize: '20px',
            backgroundPositionX: '97%',
            backgroundPositionY: 'center',
            cursor: 'auto'
          }}
          suppressHydrationWarning={true}
        />
        <IconComponent
          className="absolute left-4 top-1/2 transform -translate-y-1/2 text-muted-foreground"
          size={20}
        />
        {showPasswordToggle && onTogglePassword && (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            className="absolute right-2 top-1/2 transform -translate-y-1/2 h-10 w-10 text-muted-foreground hover:text-foreground hover:bg-muted/50 transition-colors"
            onClick={onTogglePassword}
          >
            {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
          </Button>
        )}
      </div>
    </div>
  );
}