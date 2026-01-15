import { RecipeEntry, Settings, PromptVersion } from '../types/recipe';

export const defaultSettings: Settings = {
  tavilyApiKey: 'tvly-YOUR_API_KEY_HERE',
  openaiApiKey: 'sk-YOUR_OPENAI_KEY_HERE',
  selectedModel: 'gpt-4o-mini',
  systemPrompt: `Ты — эксперт по структурированию кулинарных рецептов. Твоя задача — извлечь из текста рецепта следующую информацию в формате JSON:

{
  "dishName": "Название блюда",
  "cookingTime": число_минут,
  "servings": количество_порций,
  "ingredients": [
    {
      "name": "Название ингредиента",
      "amount": "количество",
      "unit": "единица измерения"
    }
  ],
  "steps": ["Шаг 1", "Шаг 2", ...]
}

Требования:
- Извлекай точные количества и единицы измерения
- Нормализуй единицы (мл, г, шт и т.д.)
- Разбивай инструкцию на логические шаги
- Если информация отсутствует, используй null`,
  temperature: 0.3,
  maxTokens: 2000
};

// Fallback recipe data - second sample from tavily_responce.txt (index 1)
// This is kept as a constant for reference but not used in the app
// The actual fallback is stored in the database via backend/init_db.py
export const FALLBACK_RECIPE_DATA = {
  query: "рецепт салата оливье",
  tavilyResponse: {
    url: "https://www.russianfood.com/recipes/bytype/?fid=746",
    title: "Салат Оливье, рецепты на RussianFood.com",
    content: "Очень вкусный рецепт салата \"Оливье\". Продукты: язык говяжий, картофель, морковь, огурцы солёные, яйца, горошек зелёный консервированный, соль, перец чёрный мо",
    score: 0.902481
  }
};

// Empty array - recipes are now loaded from API
export const mockRecipes: RecipeEntry[] = [];

export const mockPromptVersions: PromptVersion[] = [
  {
    version: 'v1.2',
    date: '2026-01-10',
    changes: 'Добавлена нормализация единиц измерения, улучшена обработка диапазонов',
    effectOnMetrics: '+8% точность ингредиентов'
  },
  {
    version: 'v1.1',
    date: '2026-01-05',
    changes: 'Оптимизирован парсинг шагов приготовления',
    effectOnMetrics: '+5% полнота данных'
  },
  {
    version: 'v1.0',
    date: '2026-01-01',
    changes: 'Базовая версия промпта',
    effectOnMetrics: 'Baseline'
  }
];

export const mockAnalytics = {
  successRate: 85,
  averageScores: {
    ingredientAccuracy: 4.3,
    dataCompleteness: 4.1,
    originalMatch: 4.5,
    overallQuality: 4.2
  },
  topErrors: [
    { type: 'Единицы измерения', count: 12, percentage: 35 },
    { type: 'Пропущенные ингредиенты', count: 8, percentage: 24 },
    { type: 'Неточные количества', count: 7, percentage: 20 },
    { type: 'Другое', count: 7, percentage: 21 }
  ],
  totalRecipes: 47,
  processedRecipes: 40,
  readyForProduction: 32
};
