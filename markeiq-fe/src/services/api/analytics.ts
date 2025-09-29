import { makeRequest } from '@/services/utils';

export interface AnalyticsDashboard {
  timestamp: string;
  generation_time_ms: number;
  status: string;
  catalog: {
    total_products: number;
    total_variants: number;
    brand_distribution: {
      brand: string;
      products: number;
      variants: number;
    }[];
    availability_distribution: {
      status: string;
      count: number;
    }[];
  };
  pricing: {
    products: {
      total_priced_products: number;
      min_price: number;
      max_price: number;
      avg_price: number;
    };
    variants: {
      total_priced_variants: number;
      min_price: number;
      max_price: number;
      avg_price: number;
    };
    price_range_summary: {
      min: number;
      max: number;
      avg_product: number;
      avg_variant: number;
    };
  };
  reviews: {
    total_reviews: number;
    avg_rating: number;
    min_rating: number;
    max_rating: number;
  };
  customer_activity: {
    recent_reviews_30d: number;
    avg_rating: number;
    review_coverage: number;
  };
  users: {
    total_users: number;
    recent_logins_30d: number;
    new_users_7d: number;
    user_engagement: {
      login_rate: number;
      growth_rate: number;
    };
  };
  system: {
    database: {
      status: string;
      response_time_ms: number;
    };
    resources: {
      cpu_usage_percent: number;
      memory_usage_percent: number;
      memory_available_gb: number;
      disk_free_gb: number;
      disk_usage_percent: number;
    };
    overall_status: string;
  };
  trends: {
    products: {
      current_total: number;
      growth_trend: string;
    };
    users: {
      current_total: number;
      new_this_week: number;
      growth_trend: string;
    };
    reviews: {
      current_total: number;
      recent_activity: number;
      growth_trend: string;
    };
  };
  quick_stats: {
    total_products: number;
    total_users: number;
    total_reviews: number;
    avg_rating: number;
    system_health: string;
    recent_activity: {
      new_reviews: number;
      new_users: number;
      active_logins: number;
    };
  };
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  timestamp: string;
  refresh_interval: number;
}

export class AnalyticsService {

  static async getDashboardData(): Promise<AnalyticsDashboard> {
    
    // Uncomment this when you have a real API endpoint:
    const response = await makeRequest<AnalyticsDashboard>('/api/v1/dashboard', {
      method: 'GET',
    });
    return response;
  }

}