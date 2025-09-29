"use client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertTriangle, HomeIcon, Mail } from "lucide-react";
import Link from "next/link";
import React from "react";

export default function NotFoundPage() {
    return (
        <div className="flex h-screen items-center justify-center">
            <Card className="h-full w-full shadow-lg rounded-none border-none dark:bg-[#141414] bg-white flex items-center justify-center">
                <CardHeader className="text-center w-full">
                    <CardTitle className="flex flex-col items-center gap-3 text-2xl">
                        <AlertTriangle
                            className="h-12 w-12 text-destructive transition-transform hover:scale-110"
                            aria-hidden="true"
                        />
                        404 - Page Not Found
                    </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6 text-center">
                    <div className="space-y-2">
                        <p className="text-base text-muted-foreground">
                            Sorry, the page you’re looking for doesn’t exist or
                            has been moved.
                        </p>
                        <p className="text-sm text-muted-foreground">
                            This could be due to a mistyped URL, an outdated
                            link, or the page being removed. Please check the
                            URL or try one of the options below.
                        </p>
                        <p className="text-xs text-muted-foreground">
                            Error Code: 404
                        </p>
                    </div>
                    <div className="flex gap-4 items-center justify-center flex-col sm:flex-row">
                        <Link
                            className="rounded-full border border-solid border-transparent transition-colors flex items-center justify-center bg-foreground text-background gap-2 hover:bg-[#383838] dark:hover:bg-[#ccc] font-medium text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5 sm:w-auto"
                            href="/"
                        >
                            <HomeIcon />
                            Got to Home
                        </Link>
                        <Link
                            className="rounded-full border border-solid border-black/[.08] dark:border-white/[.145] transition-colors flex items-center justify-center gap-2 hover:bg-[#f2f2f2] dark:hover:bg-[#1a1a1a] hover:border-transparent font-medium text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5 w-full sm:w-auto "
                            href="/contact"
                        >
                            <Mail />
                            Contact Support
                        </Link>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
