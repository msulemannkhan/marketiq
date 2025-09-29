import { makeRequest } from '@/services/utils';
import {
  Product,
  ProductListResponse,
  ProductVariantsResponse,
  ProductReviewsResponse,
  PriceHistoryResponse,
  ProductQAResponse,
  ProductOffersResponse,
  ProductSearchParams,
  ProductSearchResult
} from '@/types/product';

// Define a type for the raw product data received directly from the API for the getProducts endpoint
interface RawProductImage {
  url: string;
  alt: string;
}

interface RawProduct {
  id: string;
  name: string;
  brand: string;
  model: string;
  base_price: number;
  original_price?: number;
  currency: string;
  availability: string;
  category?: string;
  description?: string;
  image_url?: string; // Keep for backward compatibility
  product_images?: RawProductImage[]; // New format with multiple images
  pdf_spec_url?: string;
  specs: {
    processor: string;
    memory: string;
    storage: string;
    display: string;
    graphics: string;
    battery: string;
    weight: string;
  };
  rating: number;
  review_count: number;
  created_at?: string;
  updated_at?: string;
}

// Define a type for the actual single product API response format
interface SingleProductResponse {
  id: string;
  brand: string;
  model_family: string;
  base_sku: string;
  product_name: string;
  product_url: string;
  product_images: RawProductImage[];
  pdf_spec_url: string;
  base_price: string;
  original_price: string;
  status: string;
  badges: unknown[];
  offers: unknown[];
  created_at: string;
  updated_at: string;
  variants: unknown[];
}

// Define a type for the raw API response structure for the getProducts endpoint
interface RawProductListApiResponse {
  products: RawProduct[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
  has_more: boolean;
  filters_applied: Record<string, unknown>;
  facets: {
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

// Define a type for the review analysis data structure
interface ReviewAnalysisData {
  sentiment_score: number;
  keywords: string[];
  summary: string;
}

// Define a type for the review analysis API response
interface ReviewAnalysisResponse {
  success: boolean;
  data: ReviewAnalysisData;
}

export class ProductService {

  // Get all products with filtering and pagination
  static async getProducts(params?: ProductSearchParams): Promise<ProductSearchResult> {
    const searchParams = new URLSearchParams();

    // Add basic parameters
    if (params?.query) searchParams.append('query', params.query);
    if (params?.page) searchParams.append('page', params.page.toString());
    if (params?.limit) searchParams.append('limit', params.limit.toString());
    if (params?.sort_by) searchParams.append('sort_by', params.sort_by);

    // Add filters in a simplified way
    if (params?.filters) {
      const filters = params.filters;
      
      // Array filters
      if (filters.brands?.length) {
        searchParams.append('brands', filters.brands.join(','));
      }
      if (filters.processors?.length) {
        searchParams.append('processors', filters.processors.join(','));
      }
      if (filters.memory?.length) {
        searchParams.append('memory', filters.memory.join(','));
      }
      if (filters.storage?.length) {
        searchParams.append('storage', filters.storage.join(','));
      }
      if (filters.display_sizes?.length) {
        searchParams.append('display_sizes', filters.display_sizes.join(','));
      }
      if (filters.availability?.length) {
        searchParams.append('availability', filters.availability.join(','));
      }
      if (filters.categories?.length) {
        searchParams.append('categories', filters.categories.join(','));
      }
      
      // Simple value filters
      if (filters.price_min !== undefined) {
        searchParams.append('price_min', filters.price_min.toString());
      }
      if (filters.price_max !== undefined) {
        searchParams.append('price_max', filters.price_max.toString());
      }
      if (filters.ratings !== undefined) {
        searchParams.append('min_rating', filters.ratings.toString());
      }
    }

    const queryString = searchParams.toString();
    const endpoint = `/api/v1/products${queryString ? `?${queryString}` : ''}`;

    // Debug: Log the final endpoint URL
    console.log('Final API endpoint:', endpoint);
    console.log('Query parameters:', Object.fromEntries(searchParams.entries()));

    // Get raw API response
    const apiResponse = await makeRequest<RawProductListApiResponse>(endpoint);

    // Transform API response to match our interface
    const transformedProducts: Product[] = apiResponse.products?.map((product: RawProduct): Product => ({
      id: product.id,
      name: product.name,
      brand: product.brand,
      model: product.model,
      base_price: product.base_price,
      original_price: product.original_price,
      currency: product.currency,
      availability: product.availability,
      category: 'laptop',
      description: product.description || `${product.brand} ${product.model}`,
      // Handle new product_images format, fallback to image_url for backward compatibility
      image_url: product.product_images?.[0]?.url || product.image_url || '/images/products/laptop-default.png',
      product_images: product.product_images?.map(img => ({
        url: img.url,
        alt: img.alt
      })) || [],
      pdf_spec_url: product.pdf_spec_url,
      specs: {
        processor: product.specs.processor,
        memory: product.specs.memory,
        storage: product.specs.storage,
        display: product.specs.display,
        graphics: product.specs.graphics,
        battery: product.specs.battery,
        weight: product.specs.weight,
        // Optional fields for backward compatibility
        processor_brand: product.specs.processor?.split(' ')[0] || '',
        processor_model: product.specs.processor || '',
        storage_type: product.specs.storage?.includes('SSD') ? 'SSD' : 'HDD',
        display_size: product.specs.display || '',
        display_resolution: 'FHD',
        display_type: 'LCD',
        connectivity: [],
        ports: [],
        dimensions: '',
        operating_system: 'Windows 11',
        warranty: '1 year'
      },
      rating: product.rating,
      review_count: product.review_count,
      created_at: product.created_at || new Date().toISOString(),
      updated_at: product.updated_at || new Date().toISOString()
    })) || [];

    // Use API pagination data directly
    return {
      products: transformedProducts,
      total: apiResponse.total,
      page: apiResponse.page,
      limit: apiResponse.limit,
      total_pages: apiResponse.total_pages,
      has_more: apiResponse.has_more,
      filters_applied: apiResponse.filters_applied || params?.filters || {},
      facets: apiResponse.facets
    };
  }

  // Get specific product details
  static async getProduct(productId: string): Promise<Product> {
    try {
      console.log('Fetching product with ID:', productId);
      const response = await makeRequest<SingleProductResponse>(`/api/v1/products/${productId}`);
      console.log('Product API response:', response);
      
      // Transform the single product response to our Product interface
      const product: Product = {
        id: response.id,
        name: response.product_name,
        brand: response.brand,
        model: response.model_family,
        base_price: parseFloat(response.base_price),
        original_price: response.original_price ? parseFloat(response.original_price) : undefined,
        currency: 'USD', // Default currency since it's not in the response
        availability: response.status,
        category: 'laptop',
        description: `${response.brand} ${response.model_family} - ${response.product_name}`,
        image_url: response.product_images?.[0]?.url || '/images/products/laptop-default.png',
        product_images: response.product_images?.map(img => ({
          url: img.url,
          alt: img.alt || response.product_name
        })) || [],
        pdf_spec_url: response.pdf_spec_url,
        specs: {
          processor: 'Intel Core Processor', // Default since not in response
          memory: '16GB', // Default since not in response
          storage: '512GB SSD', // Default since not in response
          display: '14" Display', // Default since not in response
          graphics: 'Integrated Graphics', // Default since not in response
          battery: 'Up to 10 hours', // Default since not in response
          weight: '2.5 lbs', // Default since not in response
          // Optional fields for backward compatibility
          processor_brand: 'Intel',
          processor_model: 'Intel Core Processor',
          storage_type: 'SSD',
          display_size: '14"',
          display_resolution: 'FHD',
          display_type: 'LCD',
          connectivity: [],
          ports: [],
          dimensions: '',
          operating_system: 'Windows 11',
          warranty: '1 year'
        },
        rating: 4.5, // Default rating since not in response
        review_count: 0, // Default since not in response
        created_at: response.created_at,
        updated_at: response.updated_at
      };
      
      console.log('Transformed product:', product);
      return product;
    } catch (error) {
      console.error('Error fetching product:', error);
      throw error;
    }
  }

  // Get product variants
  static async getProductVariants(productId: number): Promise<ProductVariantsResponse['data']> {
    const response = await makeRequest<ProductVariantsResponse>(`/api/v1/products/${productId}/variants`);
    return response.data;
  }

  // Get product reviews
  static async getProductReviews(productId: number, page = 1, limit = 10): Promise<ProductReviewsResponse['data']> {
    const response = await makeRequest<ProductReviewsResponse>(
      `/api/v1/products/${productId}/reviews?page=${page}&limit=${limit}`
    );
    return response.data;
  }

  // Get review sentiment analysis
  static async getReviewAnalysis(productId: number): Promise<ReviewAnalysisResponse['data']> {
    const response = await makeRequest<ReviewAnalysisResponse>(`/api/v1/products/${productId}/reviews/analysis`);
    return response.data;
  }

  // Get price history
  static async getPriceHistory(productId: number): Promise<PriceHistoryResponse['data']> {
    const response = await makeRequest<PriceHistoryResponse>(`/api/v1/products/${productId}/price-history`);
    return response.data;
  }

  // Get product Q&A
  static async getProductQA(productId: number): Promise<ProductQAResponse['data']> {
    const response = await makeRequest<ProductQAResponse>(`/api/v1/products/${productId}/qa`);
    return response.data;
  }

  // Get product offers and deals
  static async getProductOffers(productId: number): Promise<ProductOffersResponse['data']> {
    const response = await makeRequest<ProductOffersResponse>(`/api/v1/products/${productId}/offers`);
    return response.data;
  }

  // Search products (basic)
  static async searchProducts(query: string, filters?: ProductSearchParams['filters']): Promise<ProductSearchResult> {
    const response = await makeRequest<ProductListResponse>('/api/v1/search', {
      method: 'POST',
      body: JSON.stringify({ query, filters })
    });
    return response.data;
  }

  // Advanced search with filters
  static async advancedSearch(params: ProductSearchParams): Promise<ProductSearchResult> {
    const searchParams = new URLSearchParams();

    if (params.query) searchParams.append('query', params.query);
    if (params.page) searchParams.append('page', params.page.toString());
    if (params.limit) searchParams.append('limit', params.limit.toString());
    if (params.sort_by) searchParams.append('sort_by', params.sort_by);

    // Add all filter parameters
    if (params.filters) {
      Object.entries(params.filters).forEach(([key, value]) => {
        if (Array.isArray(value)) {
          searchParams.append(key, value.join(','));
        } else if (value !== undefined && value !== null) {
          searchParams.append(key, value.toString());
        }
      });
    }

    const response = await makeRequest<ProductListResponse>(`/api/v1/search/advanced?${searchParams.toString()}`);
    return response.data;
  }

  // Semantic AI-powered search
  static async semanticSearch(query: string, context?: string): Promise<ProductSearchResult> {
    const response = await makeRequest<ProductListResponse>('/api/v1/search/semantic', {
      method: 'POST',
      body: JSON.stringify({ query, context })
    });
    return response.data;
  }

  // Utility methods for common use cases
  static async getFeaturedProducts(limit = 8): Promise<Product[]> {
    const result = await this.getProducts({
      sort_by: 'popularity',
      limit,
      filters: { availability: ['in_stock'] }
    });
    return result.products;
  }

  static async getProductsByBrand(brand: string, limit = 12): Promise<Product[]> {
    const result = await this.getProducts({
      filters: { brands: [brand] },
      limit,
      sort_by: 'popularity'
    });
    return result.products;
  }

  static async getProductsInPriceRange(minPrice: number, maxPrice: number): Promise<Product[]> {
    const result = await this.getProducts({
      filters: {
        price_min: minPrice,
        price_max: maxPrice,
        availability: ['in_stock']
      },
      sort_by: 'price_asc'
    });
    return result.products;
  }

  static async getTopRatedProducts(limit = 10): Promise<Product[]> {
    const result = await this.getProducts({
      filters: { ratings: 4 },
      sort_by: 'rating',
      limit
    });
    return result.products;
  }

  // Get products by specific IDs
  static async getProductsByIds(productIds: string[]): Promise<Product[]> {
    if (productIds.length === 0) return [];
    
    // For now, we'll get all products and filter by IDs
    // In a real implementation, you might have a specific endpoint for this
    const result = await this.getProducts({ limit: 1000 }); // Get a large number to ensure we get all products
    return result.products.filter(product => productIds.includes(product.id));
  }
}