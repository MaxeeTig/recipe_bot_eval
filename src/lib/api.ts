import axios, { AxiosError, AxiosResponse } from 'axios';
import { logger } from './logger';

const API_BASE_URL = 'http://localhost:8002/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout to prevent hanging requests
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    logger.debug('API request', {
      method: config.method?.toUpperCase(),
      url: config.url,
      baseURL: config.baseURL,
    });
    return config;
  },
  (error) => {
    logger.error('API request error', { error: error.message }, error);
    return Promise.reject(error);
  }
);

// Response interceptor for logging
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    const requestId = response.headers['x-request-id'];
    logger.debug('API response', {
      method: response.config.method?.toUpperCase(),
      url: response.config.url,
      status: response.status,
      requestId,
    });
    return response;
  },
  (error: AxiosError) => {
    const requestId = error.response?.headers['x-request-id'];
    logger.error(
      'API response error',
      {
        method: error.config?.method?.toUpperCase(),
        url: error.config?.url,
        status: error.response?.status,
        statusText: error.response?.statusText,
        requestId,
        errorMessage: error.message,
      },
      error
    );
    return Promise.reject(error);
  }
);

export interface TavilyResult {
  url: string;
  title: string;
  content: string;
  score: number;
  raw_content?: string | null;
}

export interface TavilyResponse {
  query: string;
  follow_up_questions?: string[] | null;
  answer?: string;
  images?: string[];
  results: TavilyResult[];
  response_time?: number;
  request_id?: string;
}

export interface RecipeApiResponse {
  id: string;
  query: string;
  tavily_response: TavilyResponse;
  selected_result_index: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export const api = {
  // Search for a recipe
  searchRecipe: async (query: string): Promise<RecipeApiResponse> => {
    logger.debug('Calling searchRecipe API', { query });
    const response = await apiClient.post<RecipeApiResponse>('/recipes/search', { query });
    logger.debug('searchRecipe API completed', { 
      recipeId: response.data.id,
      query: response.data.query 
    });
    return response.data;
  },

  // Get all recipes
  getRecipes: async (): Promise<RecipeApiResponse[]> => {
    logger.debug('Calling getRecipes API');
    const response = await apiClient.get<RecipeApiResponse[]>('/recipes');
    logger.debug('getRecipes API completed', { count: response.data.length });
    return response.data;
  },

  // Get a single recipe
  getRecipe: async (id: string): Promise<RecipeApiResponse> => {
    logger.debug('Calling getRecipe API', { recipeId: id });
    const response = await apiClient.get<RecipeApiResponse>(`/recipes/${id}`);
    logger.debug('getRecipe API completed', { recipeId: id });
    return response.data;
  },

  // Delete a recipe (soft delete)
  deleteRecipe: async (id: string): Promise<void> => {
    logger.debug('Calling deleteRecipe API', { recipeId: id });
    await apiClient.delete(`/recipes/${id}`);
    logger.debug('deleteRecipe API completed', { recipeId: id });
  },

  // Health check
  healthCheck: async (): Promise<{ status: string; service: string }> => {
    logger.debug('Calling healthCheck API');
    const response = await apiClient.get('/health');
    logger.debug('healthCheck API completed', { status: response.data.status });
    return response.data;
  },
};
