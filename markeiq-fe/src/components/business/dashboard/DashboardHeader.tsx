"use client";

import { BRAND_CONFIG } from "@/lib/config/brand-config";
import { Button } from "@/components/ui/button";
import { Bell, Download, RotateCcw } from "lucide-react";

export function DashboardHeader() {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-8">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
        {/* Title Section */}
        <div className="space-y-2">
          <h1 className="text-2xl lg:text-3xl font-bold text-gray-900 dark:text-white tracking-tight">
            {BRAND_CONFIG.dashboard.title}
          </h1>
          <p className="text-base text-gray-600 dark:text-gray-400">
            {BRAND_CONFIG.dashboard.subtitle}
          </p>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="icon"
            className="h-10 w-10 rounded-xl border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            <Bell className="h-4 w-4" />
          </Button>

          <Button
            variant="outline"
            size="icon"
            className="h-10 w-10 rounded-xl border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            <RotateCcw className="h-4 w-4" />
          </Button>

          <Button
            variant="outline"
            className="px-4 py-2 rounded-xl border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 gap-2"
          >
            <Download className="h-4 w-4" />
            Export
          </Button>

          <Button
            className="px-6 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white shadow-sm"
          >
            Refresh Data
          </Button>
        </div>
      </div>
    </div>
  );
}