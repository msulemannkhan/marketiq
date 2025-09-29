import { AppSidebar } from "@/components/layout/AppSidebar";

export default function DashboardLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <div className="flex min-h-screen bg-background">
            <AppSidebar />
            <main className="flex-1 overflow-auto bg-background">
                {children}
            </main>
        </div>
    );
}
