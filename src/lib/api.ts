import axios, { AxiosError, AxiosResponse } from 'axios';
import { logger } from './logger';

const API_BASE_URL = (import.meta.env.VITE_API_URL as string) || 'http://localhost:8003';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
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

// --- Response types (aligned with backend schemas) ---

export interface RecipeSearchResponse {
  recipe_id: number;
  status: string;
  title: string;
  url: string;
}

export interface RecipeListItem {
  id: number;
  recipe_name: string;
  source_url: string;
  raw_title: string;
  status: string;
  created_at: string;
  updated_at: string;
  parsed_at?: string;
}

export interface RecipeDetailResponse {
  id: number;
  recipe_name: string;
  source_url: string;
  raw_title: string;
  raw_recipe_text: string[];
  status: string;
  parsed_recipe?: Record<string, unknown> | null;
  error_type?: string | null;
  error_message?: string | null;
  error_traceback?: string | null;
  llm_response_text?: string | null;
  created_at: string;
  updated_at: string;
  parsed_at?: string | null;
}

export interface RecipeStatsResponse {
  total: number;
  by_status: Record<string, number>;
  by_error_type?: Record<string, number> | null;
}

export interface AnalysisResponse {
  analysis_id: number;
  recipe_id: number;
  analysis_report: Record<string, unknown>;
  recommendations_summary?: string | null;
  created_at: string;
  reparse_result?: { status: string; parsed_recipe?: unknown; error?: unknown } | null;
}

export interface ParseResponse {
  recipe_id: number;
  status: string;
  parsed_recipe?: unknown;
  error?: Record<string, unknown> | null;
}

export const api = {
  searchRecipe: async (query: string): Promise<RecipeSearchResponse> => {
    logger.debug('Calling searchRecipe API', { query });
    const response = await apiClient.post<RecipeSearchResponse>('/api/recipes/search', { query });
    logger.debug('searchRecipe API completed', { recipeId: response.data.recipe_id, query });
    return response.data;
  },

  getRecipes: async (params?: { status_filter?: string }): Promise<RecipeListItem[]> => {
    logger.debug('Calling getRecipes API', params);
    const url = '/api/recipes';
    const response = await apiClient.get<{ recipes: RecipeListItem[]; total: number }>(
      params?.status_filter ? `${url}?status_filter=${encodeURIComponent(params.status_filter)}` : url
    );
    logger.debug('getRecipes API completed', { count: response.data.recipes?.length ?? 0 });
    return response.data.recipes ?? [];
  },

  getRecipe: async (id: string): Promise<RecipeDetailResponse> => {
    logger.debug('Calling getRecipe API', { recipeId: id });
    const response = await apiClient.get<RecipeDetailResponse>(`/api/recipes/${id}`);
    logger.debug('getRecipe API completed', { recipeId: id });
    return response.data;
  },

  deleteRecipe: async (id: string): Promise<void> => {
    logger.debug('Calling deleteRecipe API', { recipeId: id });
    await apiClient.delete(`/api/recipes/${id}`);
    logger.debug('deleteRecipe API completed', { recipeId: id });
  },

  parseRecipe: async (id: string, opts?: { model?: string; provider?: string }): Promise<ParseResponse> => {
    logger.debug('Calling parseRecipe API', { recipeId: id, opts });
    const body: { model?: string; provider?: string } = {};
    if (opts?.model) body.model = opts.model;
    if (opts?.provider) body.provider = opts.provider;
    const response = await apiClient.post<ParseResponse>(`/api/recipes/${id}/parse`, Object.keys(body).length ? body : {});
    logger.debug('parseRecipe API completed', { recipeId: id });
    return response.data;
  },

  getRecipeStats: async (params?: { date_from?: string; date_to?: string }): Promise<RecipeStatsResponse> => {
    logger.debug('Calling getRecipeStats API', params);
    const sp = new URLSearchParams();
    if (params?.date_from) sp.set('date_from', params.date_from);
    if (params?.date_to) sp.set('date_to', params.date_to);
    const qs = sp.toString();
    const response = await apiClient.get<RecipeStatsResponse>(
      qs ? `/api/recipes/stats?${qs}` : '/api/recipes/stats'
    );
    return response.data;
  },

  analyzeRecipe: async (
    id: string,
    opts?: { model?: string; provider?: string; apply_patches?: boolean; reparse?: boolean }
  ): Promise<AnalysisResponse> => {
    logger.debug('Calling analyzeRecipe API', { recipeId: id, opts });
    const body: Record<string, unknown> = {};
    if (opts?.model) body.model = opts.model;
    if (opts?.provider) body.provider = opts.provider;
    if (opts?.apply_patches != null) body.apply_patches = opts.apply_patches;
    if (opts?.reparse != null) body.reparse = opts.reparse;
    const response = await apiClient.post<AnalysisResponse>(`/api/recipes/${id}/analyze`, body);
    logger.debug('analyzeRecipe API completed', { recipeId: id });
    return response.data;
  },

  getRecipeAnalyses: async (id: string): Promise<AnalysisResponse[]> => {
    logger.debug('Calling getRecipeAnalyses API', { recipeId: id });
    const response = await apiClient.get<{ analyses: AnalysisResponse[] }>(`/api/recipes/${id}/analyses`);
    return response.data.analyses ?? [];
  },

  healthCheck: async (): Promise<{ status: string; timestamp: string }> => {
    logger.debug('Calling healthCheck API');
    const response = await apiClient.get<{ status: string; timestamp: string }>('/health');
    return response.data;
  },
};
