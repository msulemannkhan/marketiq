import { AuthLayout } from "@/components/layout/AuthLayout";
import { AuthHero, RegisterForm } from "@/components/business/auth";
import { AuthRedirect } from "@/components/auth";

export default function RegisterPage() {
  return (
    <AuthRedirect>
      <AuthLayout
        leftSide={<AuthHero />}
        rightSide={<RegisterForm />}
      />
    </AuthRedirect>
  );
}