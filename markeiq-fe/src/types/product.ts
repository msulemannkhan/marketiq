// Product core interfaces
export interface ProductImage {
  url: string;
  alt: string;
}

export interface Product {
  id: string;
  name: string;
  brand: string;
  model: string;
  base_price: number;
  original_price?: number;
  discount_percentage?: number;
  currency: string;
  availability: string;
  category?: string;
  subcategory?: string;
  description?: string;
  image_url?: string; // Keep for backward compatibility
  additional_images?: string[]; // Keep for backward compatibility
  product_images?: ProductImage[]; // New format with multiple images
  pdf_spec_url?: string;
  specs: ProductSpecs;
  rating: number;
  review_count: number;
  
  created_at?: string;
  updated_at?: string;
}

export interface ProductSpecs {
  processor: string;
  memory: string;
  storage: string;
  display: string;
  graphics: string;
  battery: string;
  weight: string;
  // Optional fields for backward compatibility
  processor_brand?: string;
  processor_model?: string;
  storage_type?: string;
  display_size?: string;
  display_resolution?: string;
  display_type?: string;
  operating_system?: string;
  connectivity?: string[];
  ports?: string[];
  dimensions?: string;
  color?: string;
  warranty?: string;
}

export interface ProductRatings {
  average_rating: number;
  total_reviews: number;
  // Changed from rating_distribution object to individual star ratings
  // to match the object literal assignment in product.ts service.
  one_star: number;
  two_star: number;
  three_star: number;
  four_star: number;
  five_star: number;
}

// Product variants (different configurations)
export interface ProductVariant {
  id: number;
  product_id: number;
  name: string;
  price: number;
  availability: string;
  specs_override: Partial<ProductSpecs>;
  image_url?: string;
}

// Product reviews
export interface ProductReview {
  id: number;
  product_id: number;
  user_name: string;
  rating: number;
  title: string;
  content: string;
  verified_purchase: boolean;
  helpful_votes: number;
  total_votes: number;
  created_at: string;
  pros?: string[];
  cons?: string[];
}

export interface ReviewAnalysis {
  sentiment_score: number;
  sentiment_label: 'positive' | 'neutral' | 'negative';
  key_topics: string[];
  pros_summary: string[];
  cons_summary: string[];
  common_complaints: string[];
  recommended_percentage: number;
}

// Price history
export interface PriceHistoryPoint {
  date: string;
  price: number;
  availability: string;
  source?: string;
}

export interface PriceHistory {
  product_id: number;
  current_price: number;
  lowest_price: number;
  highest_price: number;
  price_trend: 'up' | 'down' | 'stable';
  history: PriceHistoryPoint[];
}

// Q&A
export interface ProductQA {
  id: number;
  product_id: number;
  question: string;
  answer?: string;
  asked_by: string;
  answered_by?: string;
  asked_at: string;
  answered_at?: string;
  helpful_votes: number;
  verified_purchaser: boolean;
}

// Offers and deals
export interface ProductOffer {
  id: number;
  product_id: number;
  title: string;
  description: string;
  discount_type: 'percentage' | 'fixed_amount' | 'bundle';
  discount_value: number;
  original_price: number;
  discounted_price: number;
  valid_from: string;
  valid_until: string;
  terms_conditions?: string;
  offer_type: 'flash_sale' | 'seasonal' | 'clearance' | 'bundle' | 'loyalty';
}

// Search and filtering
export interface ProductFilters {
  brands?: string[];
  price_min?: number;
  price_max?: number;
  processors?: string[];
  memory?: string[];
  storage?: string[];
  display_sizes?: string[];
  ratings?: number;
  availability?: string[];
  categories?: string[];
}

export interface ProductSearchParams {
  query?: string;
  filters?: ProductFilters;
  sort_by?: 'price_asc' | 'price_desc' | 'rating' | 'popularity' | 'newest' | 'name';
  page?: number;
  limit?: number;
}

export interface SearchProduct {
  id: number;
  brand: string;
  model: string;
  name: string;
  base_price: number;
  currency: string;
  availability: 'in_stock' | 'out_of_stock' | 'pre_order' | 'discontinued';
  rating: number;
  review_count: number;
  pdf_spec_url: string;
  specs: {
    processor: string;
    memory: string;
    storage: string;
    display: string;
    graphics: string;
    battery: string;
    weight: string;
  };
}

export interface ProductSearchResult {
  products: Product[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
  has_more: boolean;
  filters_applied: ProductFilters & Pick<ProductSearchParams, 'sort_by'>;
  facets?: {
    brands: { name: string; count: number }[];
    price_ranges: { min: number; max: number; count: number }[];
    processors: { name: string; count: number }[];
    memory: { name: string; count: number }[];
    storage: { name: string; count: number }[];
    availability: { name: string; count: number }[];
    rating_ranges: { min: number; max: number; label: string; count: number }[];
    search_suggestions: { query: string; type: string; count: number }[];
  };
}

// API response wrappers
export interface ProductResponse {
  success: boolean;
  data: Product;
  timestamp: string;
}

export interface ProductListResponse {
  success: boolean;
  data: ProductSearchResult;
  timestamp: string;
}

export interface ProductVariantsResponse {
  success: boolean;
  data: ProductVariant[];
  timestamp: string;
}

export interface ProductReviewsResponse {
  success: boolean;
  data: {
    reviews: ProductReview[];
    analysis: ReviewAnalysis;
    total_count: number;
    page: number;
    limit: number;
  };
  timestamp: string;
}

export interface PriceHistoryResponse {
  success: boolean;
  data: PriceHistory;
  timestamp: string;
}

export interface ProductQAResponse {
  success: boolean;
  data: ProductQA[];
  timestamp: string;
}

export interface ProductOffersResponse {
  success: boolean;
  data: ProductOffer[];
  timestamp: string;
}