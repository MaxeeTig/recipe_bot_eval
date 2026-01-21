import type { Settings, RecipeEntry } from '../types/recipe';

export const defaultSettings: Settings = {
  provider: 'together_ai',
  modelParsing: '',
  modelAnalysis: '',
};

export const PROVIDERS = ['together_ai', 'vercel_ai', 'mistral_ai', 'deepseek_ai'] as const;

export const mockRecipes: RecipeEntry[] = [];
