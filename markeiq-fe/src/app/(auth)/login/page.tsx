import { AuthLayout } from "@/components/layout/AuthLayout";
import { AuthHero, LoginForm } from "@/components/business/auth";
import { AuthRedirect } from "@/components/auth";

export default function LoginPage() {
  return (
    <AuthRedirect>
      <AuthLayout
        leftSide={<AuthHero />}
        rightSide={<LoginForm />}
      />
    </AuthRedirect>
  );
}