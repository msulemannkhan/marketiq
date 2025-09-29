"use client";

import { useState } from "react";
import { BRAND_CONFIG } from "@/lib/config/brand-config";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type TabKey = keyof typeof BRAND_CONFIG.dashboard.tabs;

interface DashboardTabsProps {
  defaultTab?: TabKey;
  className?: string;
}

export function DashboardTabs({ defaultTab = "overview", className }: DashboardTabsProps) {
  const [activeTab, setActiveTab] = useState<TabKey>(defaultTab);
  const { tabs } = BRAND_CONFIG.dashboard;

  return (
    <div className={cn("w-full", className)}>
      {/* Tab Navigation */}
      <div className="flex flex-wrap gap-2 mb-8 p-1 bg-gray-100 dark:bg-gray-800 rounded-2xl">
        {Object.entries(tabs).map(([key, tab]) => (
          <Button
            key={key}
            variant="ghost"
            onClick={() => setActiveTab(key as TabKey)}
            className={cn(
              "flex-1 min-w-fit px-6 py-3 rounded-xl font-medium transition-all duration-200",
              activeTab === key
                ? "bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm"
                : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-white/50 dark:hover:bg-gray-700/50"
            )}
          >
            {tab.label}
          </Button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="min-h-[600px]">
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 p-8">
          <div className="space-y-6">
            <div className="space-y-2">
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white tracking-tight">
                {tabs[activeTab].title}
              </h1>
              <p className="text-lg text-gray-600 dark:text-gray-400 leading-relaxed">
                {tabs[activeTab].description}
              </p>
            </div>

            {/* Tab-specific content */}
            <div className="pt-8">
              {renderTabContent(activeTab)}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function renderTabContent(tab: TabKey) {
  switch (tab) {
    case "overview":
      return <OverviewContent />;
    case "catalog":
      return <CatalogContent />;
    case "analytics":
      return <AnalyticsContent />;
    case "insights":
      return <InsightsContent />;
    case "assistant":
      return <AssistantContent />;
    default:
      return <OverviewContent />;
  }
}

function OverviewContent() {
  return (
    <div className="space-y-8">
      {/* KPI Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <KPICard
          title={BRAND_CONFIG.dashboard.kpis.totalProducts}
          value="1,247"
          change="+12%"
          trend="up"
          description="Products tracked across all brands"
        />
        <KPICard
          title={BRAND_CONFIG.dashboard.kpis.avgPrice}
          value="$1,489"
          change="-3.2%"
          trend="down"
          description="Average price of business laptops"
        />
        <KPICard
          title={BRAND_CONFIG.dashboard.kpis.topBrands}
          value="HP, Lenovo"
          change="Top 2"
          trend="neutral"
          description="Leading marketplace brands"
        />
        <KPICard
          title={BRAND_CONFIG.dashboard.kpis.reviewScore}
          value="4.2/5"
          change="+0.3"
          trend="up"
          description="Average customer satisfaction"
        />
        <KPICard
          title={BRAND_CONFIG.dashboard.kpis.availability}
          value="87%"
          change="+5%"
          trend="up"
          description="Products currently in stock"
        />
        <KPICard
          title={BRAND_CONFIG.dashboard.kpis.priceChange}
          value="-2.1%"
          change="24h"
          trend="down"
          description="Market price movement"
        />
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border border-blue-200 dark:border-blue-700 rounded-2xl p-6">
          <h3 className="text-xl font-semibold mb-4 text-blue-900 dark:text-blue-100">Recent Trends</h3>
          <p className="text-blue-700 dark:text-blue-300 mb-4">
            Business laptop prices have decreased by 2.1% in the last 24 hours across all monitored marketplaces.
          </p>
          <Button variant="outline" className="border-blue-300 text-blue-700 hover:bg-blue-200 dark:border-blue-600 dark:text-blue-300 rounded-xl">
            View Details
          </Button>
        </div>

        <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border border-green-200 dark:border-green-700 rounded-2xl p-6">
          <h3 className="text-xl font-semibold mb-4 text-green-900 dark:text-green-100">AI Insights</h3>
          <p className="text-green-700 dark:text-green-300 mb-4">
            New HP and Lenovo models show strong customer satisfaction. Consider updating recommendations.
          </p>
          <Button variant="outline" className="border-green-300 text-green-700 hover:bg-green-200 dark:border-green-600 dark:text-green-300 rounded-xl">
            Ask AI Assistant
          </Button>
        </div>
      </div>
    </div>
  );
}

function CatalogContent() {
  return (
    <div className="space-y-6">
      <div className="text-center py-12">
        <h3 className="text-2xl font-semibold text-muted-foreground mb-4">Product Catalog</h3>
        <p className="text-lg text-muted-foreground">
          Browse and compare business laptops across multiple marketplace brands.
        </p>
        <div className="mt-8">
          <Button size="lg" className="px-8 py-4">
            Coming Soon
          </Button>
        </div>
      </div>
    </div>
  );
}

function AnalyticsContent() {
  return (
    <div className="space-y-6">
      <div className="text-center py-12">
        <h3 className="text-2xl font-semibold text-muted-foreground mb-4">Price Analytics</h3>
        <p className="text-lg text-muted-foreground">
          Historical pricing trends and market analysis across all brands.
        </p>
        <div className="mt-8">
          <Button size="lg" className="px-8 py-4">
            Coming Soon
          </Button>
        </div>
      </div>
    </div>
  );
}

function InsightsContent() {
  return (
    <div className="space-y-6">
      <div className="text-center py-12">
        <h3 className="text-2xl font-semibold text-muted-foreground mb-4">Market Insights</h3>
        <p className="text-lg text-muted-foreground">
          Customer feedback and market sentiment analysis.
        </p>
        <div className="mt-8">
          <Button size="lg" className="px-8 py-4">
            Coming Soon
          </Button>
        </div>
      </div>
    </div>
  );
}

function AssistantContent() {
  return (
    <div className="space-y-6">
      <div className="text-center py-12">
        <h3 className="text-2xl font-semibold text-muted-foreground mb-4">AI Assistant</h3>
        <p className="text-lg text-muted-foreground">
          Get personalized laptop recommendations powered by AI.
        </p>
        <div className="mt-8">
          <Button size="lg" className="px-8 py-4">
            Open Chat Interface
          </Button>
        </div>
      </div>
    </div>
  );
}

interface KPICardProps {
  title: string;
  value: string;
  change: string;
  trend: "up" | "down" | "neutral";
  description: string;
}

function KPICard({ title, value, change, trend, description }: KPICardProps) {
  const trendColors = {
    up: "text-green-600 dark:text-green-400",
    down: "text-red-600 dark:text-red-400",
    neutral: "text-gray-500 dark:text-gray-400"
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 hover:shadow-md transition-all duration-200">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-gray-500 dark:text-gray-400 text-sm uppercase tracking-wide">
            {title}
          </h3>
          <span className={cn("text-sm font-medium", trendColors[trend])}>
            {change}
          </span>
        </div>
        <div className="space-y-2">
          <div className="text-3xl font-bold text-gray-900 dark:text-white tracking-tight">
            {value}
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {description}
          </p>
        </div>
      </div>
    </div>
  );
}