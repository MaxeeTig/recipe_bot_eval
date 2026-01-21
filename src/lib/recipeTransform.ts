import type { RecipeSearchResponse, RecipeListItem, RecipeDetailResponse } from './api';
import type { RecipeEntry, RecipeData, RecipeSource, Ingredient } from '../types/recipe';

/**
 * Transform backend parsed recipe to frontend RecipeData format
 */
export function backendRecipeToFrontendRecipeData(
  backendRecipe: { title?: string; ingredients?: Array<{ name?: string; amount?: number; unit?: string; original_text?: string }>; instructions?: string[]; cooking_time?: number; servings?: number },
  recipeId: string,
  metadata: { promptVersion?: string; modelUsed?: string; searchDate: string }
): RecipeData {
  const ingredients: Ingredient[] = (backendRecipe.ingredients || []).map((ing) => ({
    name: ing.name || '',
    amountLLM: String(ing.amount ?? ''),
    unitLLM: ing.unit || '',
    original: ing.original_text || '',
    isCorrect: true,
  }));

  return {
    id: recipeId,
    dishName: backendRecipe.title || '',
    cookingTime: backendRecipe.cooking_time || 0,
    servings: backendRecipe.servings || 1,
    ingredients,
    steps: backendRecipe.instructions || [],
    promptVersion: metadata.promptVersion || 'v1.0',
    modelUsed: metadata.modelUsed || '—',
    searchDate: metadata.searchDate,
  };
}

function mapStatus(s: string): RecipeEntry['status'] {
  if (s === 'new') return 'pending';
  if (s === 'success') return 'processed';
  if (s === 'failure') return 'error';
  return 'processed';
}

/**
 * Convert search response to RecipeEntry (minimal, right after search)
 */
export function searchResponseToRecipeEntry(res: RecipeSearchResponse, query: string): RecipeEntry {
  return {
    id: String(res.recipe_id),
    query,
    dishName: res.title,
    date: new Date().toISOString(),
    status: 'pending',
    source: { url: res.url, rawText: '', searchQuery: query },
    recipeData: undefined,
  };
}

/**
 * Convert list item to RecipeEntry (no source/recipeData in list)
 */
export function listItemToRecipeEntry(r: RecipeListItem): RecipeEntry {
  return {
    id: String(r.id),
    query: r.recipe_name,
    dishName: r.raw_title,
    date: r.created_at,
    status: mapStatus(r.status),
    source: undefined,
    recipeData: undefined,
  };
}

/**
 * Convert recipe detail to RecipeEntry (full: source, recipeData when parsed, error when failure)
 */
export function detailToRecipeEntry(r: RecipeDetailResponse): RecipeEntry {
  const status = mapStatus(r.status);
  const source: RecipeSource = {
    url: r.source_url,
    rawText: (r.raw_recipe_text || []).join('\n\n'),
    searchQuery: r.recipe_name,
  };

  let recipeData: RecipeData | undefined;
  const pr = r.parsed_recipe;
  if (pr && typeof pr === 'object' && (pr.ingredients || pr.title)) {
    recipeData = backendRecipeToFrontendRecipeData(
      pr as Parameters<typeof backendRecipeToFrontendRecipeData>[0],
      String(r.id),
      { searchDate: r.created_at }
    );
  }

  const entry: RecipeEntry = {
    id: String(r.id),
    query: r.recipe_name,
    dishName: r.raw_title,
    date: r.created_at,
    status,
    source,
    recipeData,
  };

  if (r.status === 'failure' && (r.error_type || r.error_message)) {
    entry.error = { type: r.error_type || 'Error', message: r.error_message || '' };
  }

  return entry;
}
