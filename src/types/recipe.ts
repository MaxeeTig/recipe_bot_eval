export interface Ingredient {
  name: string;
  amountLLM: string;
  unitLLM: string;
  original: string;
  isCorrect: boolean;
}

export interface RecipeData {
  id: string;
  dishName: string;
  cookingTime: number;
  servings: number;
  ingredients: Ingredient[];
  steps: string[];
  promptVersion: string;
  modelUsed: string;
  searchDate: string;
}

export interface RecipeSource {
  url: string;
  rawText: string;
  searchQuery: string;
}

export interface RecipeEntry {
  id: string;
  query: string;
  dishName: string;
  date: string;
  status: 'processed' | 'pending' | 'error' | 'deleted';
  source?: RecipeSource;
  recipeData?: RecipeData;
  feedback?: RecipeFeedback;
}

export interface RecipeFeedback {
  ingredientAccuracy: number;
  dataCompleteness: number;
  originalMatch: number;
  overallQuality: number;
  comments: string;
  readyForProduction: boolean;
}

export interface Settings {
  tavilyApiKey: string;
  openaiApiKey: string;
  selectedModel: string;
  systemPrompt: string;
  temperature: number;
  maxTokens: number;
}

export interface PromptVersion {
  version: string;
  date: string;
  changes: string;
  effectOnMetrics: string;
}
