"use client";

import { useEffect, useState } from "react";
import { AnalyticsService, AnalyticsDashboard } from "@/services/api/analytics";
import { Package, Users, DollarSign, Star, TrendingUp, Filter, Activity, Calendar, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";

interface CircularProgressProps {
  value: number;
  max: number;
  size: number;
  strokeWidth: number;
  color: string;
}

function CircularProgress({ value, max, size, strokeWidth, color }: CircularProgressProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const progress = (value / max) * 100;
  const strokeDashoffset = circumference - (progress / 100) * circumference;

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg
        className="transform -rotate-90"
        width={size}
        height={size}
      >
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          fill="transparent"
          className="text-gray-200 dark:text-gray-700"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          className="transition-all duration-1000 ease-out"
        />
      </svg>
    </div>
  );
}

export default function PriceAnalyticsPage() {
  const [data, setData] = useState<AnalyticsDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState<number>(0);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const dashboardData = await AnalyticsService.getDashboardData();
        setData(dashboardData);
      } catch (error: unknown) {
        console.error('Failed to fetch analytics data:', error);

        // Provide more specific error messages
        if (error instanceof Error) {
          if (error.message?.includes('CORS')) {
            setError('CORS policy is blocking the request. Backend configuration needed.');
          } else if (error.message?.includes('401') || error.message?.includes('403')) {
            setError('Authentication failed. Please check your login credentials.');
          } else if (error.message?.includes('404')) {
            setError('Analytics endpoint not found. Please check the API configuration.');
          } else if (error.message?.includes('500')) {
            setError('Server error. The analytics service is temporarily unavailable.');
          } else if (error.message?.includes('fetch')) {
            setError('Network connection failed. Please check your internet connection.');
          } else {
            setError('Unable to load analytics data. Please try again later.');
          }
        } else {
          setError('Unable to load analytics data. Please try again later.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [retryCount]);

  const handleRetry = () => {
    setRetryCount(prev => prev + 1);
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 dark:bg-[#232323] rounded w-1/3 mb-2"></div>
          <div className="h-4 bg-gray-200 dark:bg-[#232323] rounded w-1/2 mb-8"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-40 bg-gray-200 dark:bg-[#232323] rounded-2xl"></div>
            ))}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 h-96 bg-gray-200 dark:bg-[#232323] rounded-2xl"></div>
            <div className="h-96 bg-gray-200 dark:bg-[#232323] rounded-2xl"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-6 space-y-8 min-h-screen bg-background">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-5xl font-bold text-foreground tracking-tight">
              Analytics
            </h1>
            <p className="mt-2 text-muted-foreground text-lg">
              Real-time marketplace insights and performance metrics
            </p>
          </div>
          <Button variant="outline" className="gap-2">
            <Filter className="h-4 w-4" />
            Filter
          </Button>
        </div>

        {/* Error State */}
        <div className="min-h-[60vh] flex items-center justify-center">
          <div className="text-center max-w-md mx-auto">
            <div className="w-16 h-16 mx-auto mb-4 bg-red-100 dark:bg-red-500/20 rounded-full flex items-center justify-center">
              <Activity className="h-8 w-8 text-red-500 dark:text-red-400" />
            </div>
            <h3 className="text-xl font-semibold text-foreground mb-2">
              Connection Issue
            </h3>
            <p className="text-muted-foreground mb-6">
              We&apos;re having trouble connecting to the analytics service. This might be due to:
            </p>
            <div className="text-left bg-card border border-border rounded-xl p-4 mb-6">
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 bg-muted-foreground rounded-full"></div>
                  CORS policy configuration
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 bg-muted-foreground rounded-full"></div>
                  Authentication requirements
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 bg-muted-foreground rounded-full"></div>
                  Network connectivity issues
                </li>
              </ul>
            </div>
            <div className="flex gap-3 justify-center">
              <Button
                onClick={handleRetry}
                className="gap-2"
                disabled={loading}
              >
                <TrendingUp className="h-4 w-4" />
                {loading ? 'Retrying...' : 'Try Again'}
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  // You can add navigation to docs or contact
                  console.log('Navigate to help/docs');
                }}
                className="gap-2"
              >
                Get Help
              </Button>
            </div>
            {error && (
              <details className="mt-6 text-left">
                <summary className="text-sm text-gray-500 dark:text-gray-400 cursor-pointer hover:text-gray-700 dark:hover:text-gray-300">
                  Technical Details
                </summary>
                <div className="mt-2 p-3 bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800 rounded-lg">
                  <code className="text-xs text-red-700 dark:text-red-300 break-all">
                    {error}
                  </code>
                </div>
              </details>
            )}
          </div>
        </div>
      </div>
    );
  }

  const kpiCards = [
    {
      title: "Total Products",
      value: data?.catalog?.total_products || 0,
      max: 600,
      icon: Package,
      color: "#000",
      bgColor: "bg-gray-50 dark:bg-[#171717]"
    },
    {
      title: "Total Reviews",
      value: data?.reviews?.total_reviews || 0,
      max: 500,
      icon: Star,
      color: "#8b5cf6",
      bgColor: "bg-purple-50 dark:bg-purple-900/20"
    },
    {
      title: "In Stock",
      value: data?.catalog?.availability_distribution?.find(item => item.status === "In Stock")?.count || 0,
      max: 200,
      icon: Activity,
      color: "#10b981",
      bgColor: "bg-green-50 dark:bg-green-900/20"
    },
    {
      title: "Average Price",
      value: Math.round(data?.pricing?.products?.avg_price || 0),
      max: 2000,
      icon: DollarSign,
      color: "#3b82f6",
      bgColor: "bg-blue-50 dark:bg-blue-900/20",
      prefix: "$"
    }
  ];

  // Only calculate if data exists
  const brandEntries = data?.catalog?.brand_distribution || [];

  return (
    <div className="p-6 space-y-8 min-h-screen bg-background">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-5xl font-bold text-foreground tracking-tight">
            Analytics
          </h1>
          <p className="mt-2 text-muted-foreground text-lg">
            Real-time marketplace insights and performance metrics
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" className="gap-2">
            <Calendar className="h-4 w-4" />
            Last 30 days
          </Button>
          <Button
            variant="outline"
            className="gap-2"
            onClick={handleRetry}
            disabled={loading}
          >
            <RotateCcw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {kpiCards.map((kpi, index) => {
          const Icon = kpi.icon;
          const displayValue = kpi.prefix ? `${kpi.prefix}${kpi.value.toLocaleString()}` : kpi.value.toLocaleString();

          return (
            <div
              key={index}
              className={`${kpi.bgColor} rounded-2xl border p-6 relative overflow-hidden`}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="p-2 bg-white dark:bg-gray-700 rounded-xl shadow-sm">
                  <Icon className="h-6 w-6" style={{ color: kpi.color }} />
                </div>
                <CircularProgress
                  value={kpi.value}
                  max={kpi.max}
                  size={48}
                  strokeWidth={4}
                  color={kpi.color}
                />
              </div>
              <div>
                <h3 className="text-3xl font-bold text-foreground mb-1">
                  {displayValue}
                </h3>
                <p className="text-muted-foreground text-sm font-medium">
                  {kpi.title}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Balance Cards */}
        <div className="lg:col-span-2 space-y-6">
          {/* User & Rating Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Total Users Card */}
            <div className="bg-gray-50 dark:bg-[#171717] rounded-2xl border p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-gray-100 dark:bg-gray-700 rounded-xl">
                  <Users className="h-6 w-6 text-gray-600 dark:text-gray-400" />
                </div>
                <span className="text-gray-600 dark:text-gray-400 font-medium">Total Users</span>
              </div>
              <div className="text-4xl font-bold text-foreground mb-6">
                {(data?.users?.total_users || 0).toLocaleString()}
              </div>
              <Button className="w-full">
                View Details
              </Button>
            </div>

            {/* Average Rating Card */}
            <div className="bg-gray-50 dark:bg-[#171717] rounded-2xl border p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-yellow-100 dark:bg-yellow-900/20 rounded-xl">
                  <Star className="h-6 w-6 text-yellow-600" />
                </div>
                <span className="text-gray-600 dark:text-gray-400 font-medium">Average Rating</span>
              </div>
              <div className="text-4xl font-bold text-foreground mb-2">
                {(data?.reviews?.avg_rating || 0).toFixed(1)}
              </div>
              <div className="flex items-center gap-1 mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star
                    key={i}
                    className={`h-4 w-4 ${
                      i < Math.floor(data?.reviews?.avg_rating || 0)
                        ? 'text-yellow-400 fill-yellow-400'
                        : 'text-gray-300 dark:text-gray-600'
                    }`}
                  />
                ))}
              </div>
              <Button variant="outline" className="w-full">
                View Reviews
              </Button>
            </div>
          </div>

          {/* Popular Products */}
          <div className="bg-gray-50 dark:bg-[#171717] rounded-2xl border p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-foreground">
                Popular Products
              </h2>
              <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                <Activity className="h-4 w-4" />
                Latest Activity
              </div>
            </div>
            <div className="space-y-4">
              {(data?.catalog?.brand_distribution || []).map((brand, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-gray-200 dark:bg-[#282828]/70 rounded-xl">
                  <div className="flex items-center gap-4">
                    <div className="w-8 h-8 bg-gradient-to-br from-gray-600 to-gray-800 rounded-lg flex items-center justify-center text-white text-sm font-bold">
                      {brand.brand.charAt(0)}
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900 dark:text-white text-sm">
                        {brand.brand} Products
                      </h3>
                      <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
                        <span className="flex items-center gap-1">
                          <Package className="h-3 w-3 text-gray-500 dark:text-gray-400" />
                          {brand.products} products
                        </span>
                        <span className="flex items-center gap-1">
                          <Activity className="h-3 w-3 text-gray-500 dark:text-gray-400" />
                          {brand.variants} variants
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className={`h-2 w-2 rounded-full ${
                      brand.products >= 300 ? 'bg-green-500' : brand.products >= 100 ? 'bg-yellow-500' : 'bg-gray-400'
                    }`}></div>
                    <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
                      {brand.brand}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {/* Search Trends */}
          <div className="bg-gray-50 dark:bg-[#171717] rounded-2xl border p-6">
            <h2 className="text-2xl font-bold text-foreground mb-6">
              Availability Status
            </h2>
            <div className="space-y-4">
              {data?.catalog?.availability_distribution?.map((item, index) => {
                const maxCount = Math.max(...(data?.catalog?.availability_distribution?.map(item => item.count) || [1]));
                const percentage = (item.count / maxCount) * 100;

                return (
                  <div key={index} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                        {item.status}
                      </span>
                      <span className="text-sm text-gray-500 dark:text-gray-400">
                        {item.count}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-yellow-400 to-yellow-600 h-2 rounded-full transition-all duration-1000 ease-out"
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Brand Distribution */}
          <div className="bg-gray-50 dark:bg-[#171717] rounded-2xl border p-6">
            <h2 className="text-2xl font-bold text-foreground mb-6">
              Brand Distribution
            </h2>
            <div className="space-y-4">
              {brandEntries.map((brand, index) => {
                return (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-200 dark:bg-[#282828]/80 rounded-xl">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-gradient-to-br from-gray-600 to-gray-800 rounded-lg flex items-center justify-center text-white text-sm font-bold">
                        {brand.brand.charAt(0)}
                      </div>
                      <span className="font-medium text-gray-900 dark:text-white">{brand.brand}</span>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-gray-900 dark:text-white">{brand.products}</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">{brand.variants} variants</div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}