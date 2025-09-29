import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "@/styles/globals.css";
import { HeroProvider, ThemeProvider, ReduxProvider, AuthProvider } from "@/components/providers";
import { BRAND_CONFIG } from "@/lib/config/brand-config";

const geistSans = Geist({
    variable: "--font-geist-sans",
    subsets: ["latin"],
});

const geistMono = Geist_Mono({
    variable: "--font-geist-mono",
    subsets: ["latin"],
});

export const metadata: Metadata = {
    title: `${BRAND_CONFIG.name} - ${BRAND_CONFIG.tagline}`,
    description: BRAND_CONFIG.hero.subtitle,
    icons: {
        icon: "/favicon.svg",
        shortcut: "/favicon.svg",
        apple: "/favicon.svg",
    },
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en" suppressHydrationWarning>
            <body
                className={`${geistSans.variable} ${geistMono.variable} antialiased`}
                suppressHydrationWarning={true}
            >
                <ThemeProvider
                    attribute="class"
                    defaultTheme="system"
                    enableSystem
                    disableTransitionOnChange
                >
                    <ReduxProvider>
                        <AuthProvider>
                            <HeroProvider>{children}</HeroProvider>
                        </AuthProvider>
                    </ReduxProvider>
                </ThemeProvider>
            </body>
        </html>
    );
}
