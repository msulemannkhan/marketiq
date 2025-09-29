"use client";
    
import { usePathname } from "next/navigation";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { Laptop, ChevronLeft, ChevronRight } from "lucide-react";
import { sidebarLinks } from "@/lib/config/navigation";
import { BRAND_CONFIG } from "@/lib/config/brand-config";
import UserMenu from "./UserMenu";
import { useClientOnly } from "@/hooks/useClientOnly";
import { useAppSelector, useAppDispatch } from "@/lib/redux/hooks";
import { toggleSidebar } from "@/lib/redux/slices/sidebarSlice";
// Assuming @heroui/react provides a Tooltip component with a 'content' prop
import { Tooltip } from "@heroui/react";

export function AppSidebar() {
    const pathname = usePathname();
    const dispatch = useAppDispatch();
    const { isCollapsed } = useAppSelector((state) => state.sidebar);
    const mounted = useClientOnly();

    // Prevent hydration mismatch by not rendering until mounted
    if (!mounted) {
        return (
            <div 
                className={cn(
                    "flex flex-col sticky top-0 bottom-0 h-screen bg-background text-gray-900 dark:text-white border-r border-gray-200 dark:border-slate-800 transition-all duration-300",
                    isCollapsed ? "w-16" : "w-64"
                )}
                suppressHydrationWarning={true}
            >
                <div className="p-6 border-b border-gray-200 dark:border-slate-800">
                    {/* Header logo and text, centered when collapsed */}
                    <div className={cn("flex items-center gap-3", isCollapsed && "justify-center")}>
                        <div className="p-2 bg-primary/10 dark:bg-gradient-to-br dark:from-white/15 dark:to-white/10 dark:backdrop-blur-md rounded-xl border border-primary/20 dark:border-white/20 shadow-lg">
                            <Laptop className="h-6 w-6 text-primary dark:text-white" />
                        </div>
                        {!isCollapsed && (
                        <div>
                            <h2 className="text-xl font-bold text-foreground drop-shadow-sm">{BRAND_CONFIG.name}</h2>
                            <p className="text-sm text-muted-foreground font-medium w-full line-clamp-1">
                                {BRAND_CONFIG.tagline}
                            </p>
                        </div>
                        )}
                    </div>
                </div>
                <div className="flex-1 px-3 py-6 overflow-y-auto">
                    <div className="space-y-6">
                        <div className="space-y-1">
                            {!isCollapsed && (
                            <p className="text-xs font-bold text-gray-400 dark:text-slate-500 uppercase tracking-widest px-4 mb-4">
                                MENU
                            </p>
                            )}
                            <div className="space-y-1">
                                <div className="h-12 bg-gray-200 dark:bg-gray-700 rounded-2xl animate-pulse"></div>
                                <div className="h-12 bg-gray-200 dark:bg-gray-700 rounded-2xl animate-pulse"></div>
                                <div className="h-12 bg-gray-200 dark:bg-gray-700 rounded-2xl animate-pulse"></div>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="p-4 border-t border-gray-200 dark:border-slate-800 space-y-2">
                    {/* User menu skeleton, centered when collapsed */}
                    <div className={cn("flex items-center gap-4", isCollapsed && "justify-center")}>
                        <div className="w-10 h-10 bg-gray-200 dark:bg-gray-700 rounded-full animate-pulse"></div>
                        {!isCollapsed && (
                        <div className="flex flex-col gap-2">
                            <div className="h-3 w-24 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
                            <div className="h-3 w-20 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
                        </div>
                        )}
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div 
            className={cn(
                "flex flex-col sticky top-0 bottom-0 h-screen bg-background text-gray-900 dark:text-white border-r border-gray-200 dark:border-slate-800 transition-all duration-300",
                isCollapsed ? "w-16" : "w-64"
            )}
            suppressHydrationWarning={true}
        >
            {/* Header */}
            <div className="p-6 border-b border-gray-200 dark:border-slate-800">
                {/* Header logo and text, centered when collapsed */}
                <div className={cn("flex items-center gap-3", isCollapsed && "justify-center")}>
                    <div className="p-2 bg-primary/10 dark:bg-gradient-to-br dark:from-white/15 dark:to-white/10 dark:backdrop-blur-md rounded-xl border border-primary/20 dark:border-white/20 shadow-lg">
                        <Laptop className="h-6 w-6 text-primary dark:text-white" />
                    </div>
                    {!isCollapsed && (
                    <div>
                        <h2 className="text-xl font-bold text-foreground drop-shadow-sm">{BRAND_CONFIG.name}</h2>
                        <p className="text-sm text-muted-foreground font-medium w-full line-clamp-1">
                            {BRAND_CONFIG.tagline}
                        </p>
                    </div>
                    )}
                </div>
            </div>

            {/* Navigation Menu */}
            {/* Added overflow-y-auto to allow navigation links to scroll independently if they exceed available height,
                preventing the sidebar from growing beyond h-screen and pushing the footer out of view. */}
            <div className="flex-1 px-3 py-6 overflow-y-auto">
                <div className="space-y-6">
                    <div className="space-y-1">
                        {!isCollapsed && (
                        <p className="text-xs font-bold text-gray-400 dark:text-slate-500 uppercase tracking-widest px-4 mb-4">
                            MENU
                        </p>
                        )}
                        <nav className="space-y-1">
                            {sidebarLinks.map((group) => (
                                <div key={group.label} className="space-y-1">
                                    {group.items.map((item) => {
                                        const isActive = pathname === item.href || (item.href !== '/dashboard' && pathname.startsWith(item.href + '/'));
                                        
                                        // Define the Link component content
                                        const linkContent = (
                                            <Link
                                                href={item.href}
                                                className={cn(
                                                    "flex items-center text-base font-semibold transition-all duration-300 relative group",
                                                    // Conditional styling for collapsed state: center content, adjust padding and remove gap
                                                    isCollapsed ? "justify-center py-2.5 px-0 rounded-xl" : "gap-4 px-4 py-3 rounded-2xl",
                                                    isActive
                                                        ? "bg-primary text-primary-foreground"
                                                        : "text-gray-600 dark:text-slate-300 hover:bg-gray-200 dark:hover:bg-[#232323] hover:text-gray-900 dark:hover:text-white",
                                                )}
                                                // Remove the native title prop as the Tooltip component will handle it
                                            >
                                                {item.icon && (
                                                    <item.icon className={cn(
                                                        "h-5 w-5 transition-all duration-300",
                                                        isActive ? "text-primary-foreground" : "text-gray-400 dark:text-slate-400 group-hover:text-gray-700 dark:group-hover:text-white"
                                                    )} />
                                                )}
                                                {/* Only show text and active dot when sidebar is not collapsed */}
                                                {!isCollapsed && (
                                                    <>
                                                        <span className="font-medium truncate">{item.label}</span>
                                                {isActive && (
                                                    <div className="absolute right-4 w-2 h-2 bg-primary-foreground rounded-full" />
                                                        )}
                                                    </>
                                                )}
                                            </Link>
                                        );

                                        // Conditionally wrap the Link with a Tooltip when the sidebar is collapsed
                                        return isCollapsed ? (
                                            <Tooltip key={item.label} content={item.label} placement="right">
                                                {linkContent}
                                            </Tooltip>
                                        ) : (
                                            // When not collapsed, render the Link directly
                                            <div key={item.label}> {/* Use a div to hold the key when Tooltip is not present */}
                                                {linkContent}
                                            </div>
                                        );
                                    })}
                                </div>
                            ))}
                        </nav>
                    </div>
                </div>
            </div>

            {/* Footer */}
            <div className="p-4 border-t border-gray-200 dark:border-slate-800 space-y-2">
                {/* Toggle Button */}
                {isCollapsed ? (
                    <Tooltip content="Expand sidebar" placement="right">
                        <button
                            onClick={() => dispatch(toggleSidebar())}
                            className={cn(
                                "w-full flex items-center text-base font-semibold transition-all duration-300 relative group",
                                "justify-center py-2.5 px-0 rounded-xl", // Collapsed state styling
                                "text-gray-600 dark:text-slate-300 hover:bg-gray-200 dark:hover:bg-[#232323] hover:text-gray-900 dark:hover:text-white",
                            )}
                            // The title prop is removed as the Tooltip component will handle it
                        >
                            <ChevronRight className={cn(
                                "h-5 w-5 transition-all duration-300",
                                "text-gray-400 dark:text-slate-400 group-hover:text-gray-700 dark:group-hover:text-white"
                            )} />
                        </button>
                    </Tooltip>
                ) : (
                    <button
                        onClick={() => dispatch(toggleSidebar())}
                        className={cn(
                            "w-full flex items-center text-base font-semibold transition-all duration-300 relative group",
                            "gap-4 px-4 py-3 rounded-2xl", // Expanded state styling
                            "text-gray-600 dark:text-slate-300 hover:bg-gray-200 dark:hover:bg-[#232323] hover:text-gray-900 dark:hover:text-white",
                        )}
                        title="Collapse sidebar" // Keep title for accessibility when not collapsed
                    >
                        <ChevronLeft className={cn(
                            "h-5 w-5 transition-all duration-300",
                            "text-gray-400 dark:text-slate-400 group-hover:text-gray-700 dark:group-hover:text-white"
                        )} />
                        <span className="font-medium truncate">Collapse</span>
                    </button>
                )}

                {/* User Menu */}
                <UserMenu />
            </div>
        </div>
    );
}
