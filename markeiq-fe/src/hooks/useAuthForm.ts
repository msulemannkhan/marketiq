import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAppDispatch } from "@/lib/redux/hooks";
import { loginUser, registerUser } from "@/lib/redux/slices/authSlice";
import { FormValidationErrors } from "@/lib/utils/validation";
import { LoginRequest, RegisterRequest } from "@/types/auth";

interface UseAuthFormOptions {
  onSuccess?: () => void;
  onError?: (error: string) => void;
  validateForm?: (formData: LoginRequest | RegisterRequest) => FormValidationErrors;
  redirectTo?: string;
}

interface UseAuthFormReturn {
  isSubmitting: boolean;
  error: string | null;
  fieldErrors: FormValidationErrors;
  submitForm: (formData: LoginRequest | RegisterRequest) => Promise<void>;
  clearError: () => void;
  clearFieldErrors: () => void;
}

export function useAuthForm(options: UseAuthFormOptions = {}): UseAuthFormReturn {
  const {
    onSuccess,
    onError,
    validateForm,
    redirectTo = "/dashboard"
  } = options;

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<FormValidationErrors>({});
  const router = useRouter();
  const dispatch = useAppDispatch();

  const clearError = () => setError(null);
  const clearFieldErrors = () => setFieldErrors({});

  const submitForm = async (
    formData: LoginRequest | RegisterRequest
  ) => {
    setError(null);
    setFieldErrors({});
    setIsSubmitting(true);

    try {
      // Client-side validation
      if (validateForm) {
        const validationErrors = validateForm(formData);
        const hasErrors = Object.keys(validationErrors).some(
          key => validationErrors[key]
        );

        if (hasErrors) {
          setFieldErrors(validationErrors);
          setIsSubmitting(false);
          return;
        }
      }

      // Determine which action to dispatch based on form data
      let result;
      if ('login' in formData) {
        // Login form
        result = await dispatch(loginUser(formData as LoginRequest));
      } else {
        // Register form
        result = await dispatch(registerUser(formData as RegisterRequest));
      }

      // Handle response
      if (loginUser.fulfilled.match(result) || registerUser.fulfilled.match(result)) {
        if (onSuccess) {
          onSuccess();
        }
        router.push(redirectTo);
      } else if (loginUser.rejected.match(result) || registerUser.rejected.match(result)) {
        const errorMessage = result.payload as string || "Authentication failed. Please try again.";
        setError(errorMessage);
        if (onError) {
          onError(errorMessage);
        }
      }
    } catch (err: unknown) {
      let errorMessage = "An unknown error occurred";

      if (err instanceof Error) {
        errorMessage = err.message || "Something went wrong";
      }

      setError(errorMessage);
      if (onError) {
        onError(errorMessage);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return {
    isSubmitting,
    error,
    fieldErrors,
    submitForm,
    clearError,
    clearFieldErrors,
  };
}