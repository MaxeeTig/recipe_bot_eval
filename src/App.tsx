import React, { useState, useEffect } from 'react';
import { Home, Settings, BarChart3, ChefHat } from 'lucide-react';
import { HomePage } from './components/HomePage';
import { RecipeDetailPage } from './components/RecipeDetailPage';
import { SettingsPanel } from './components/SettingsPanel';
import { AnalyticsDashboard } from './components/AnalyticsDashboard';
import { RecipeEntry, RecipeData, RecipeFeedback, Settings as SettingsType } from './types/recipe';
import { mockRecipes, mockAnalytics, mockPromptVersions, defaultSettings } from './lib/mockData';
import { api, RecipeApiResponse } from './lib/api';
import { Tabs, TabsList, TabsTrigger, TabsContent } from './components/ui/tabs';
import { Toaster } from './components/ui/sonner';
import { toast } from 'sonner';
import { logger } from './lib/logger';

type ViewMode = 'home' | 'detail' | 'settings' | 'analytics';

// Convert API response to RecipeEntry
function apiResponseToRecipeEntry(apiRecipe: RecipeApiResponse): RecipeEntry {
  const selectedResult = apiRecipe.tavily_response.results[apiRecipe.selected_result_index];
  
  return {
    id: apiRecipe.id,
    query: apiRecipe.query,
    dishName: selectedResult?.title || apiRecipe.query,
    date: apiRecipe.created_at,
    status: apiRecipe.status === 'deleted' ? 'deleted' : 'processed',
    source: selectedResult ? {
      url: selectedResult.url,
      rawText: selectedResult.content,
      searchQuery: apiRecipe.query
    } : undefined
  };
}

export default function App() {
  const [viewMode, setViewMode] = useState<ViewMode>('home');
  const [recipes, setRecipes] = useState<RecipeEntry[]>(mockRecipes);
  const [selectedRecipeId, setSelectedRecipeId] = useState<string | null>(null);
  const [settings, setSettings] = useState<SettingsType>(defaultSettings);
  const [isSearching, setIsSearching] = useState(false);
  const [activeTab, setActiveTab] = useState('home');
  const [isLoadingRecipes, setIsLoadingRecipes] = useState(true);

  // Load recipes from API on mount
  useEffect(() => {
    const loadRecipes = async () => {
      try {
        setIsLoadingRecipes(true);
        logger.info('Loading recipes from API');
        const apiRecipes = await api.getRecipes();
        const recipeEntries = apiRecipes.map(apiResponseToRecipeEntry);
        setRecipes(recipeEntries);
        logger.info('Recipes loaded successfully', { count: recipeEntries.length });
      } catch (error: any) {
        logger.error('Failed to load recipes', { error }, error instanceof Error ? error : new Error(String(error)));
        const errorMessage = error.code === 'ECONNABORTED' || error.message?.includes('timeout')
          ? 'Таймаут подключения к серверу'
          : error.response?.data?.detail || 'Проверьте подключение к серверу';
        toast.error('Не удалось загрузить рецепты', {
          description: errorMessage
        });
      } finally {
        setIsLoadingRecipes(false);
      }
    };

    loadRecipes();
  }, []);

  const handleSearch = async (query: string) => {
    setIsSearching(true);
    logger.info('Recipe search initiated', { query });
    
    try {
      const apiRecipe = await api.searchRecipe(query);
      const recipeEntry = apiResponseToRecipeEntry(apiRecipe);
      
      setRecipes((prev) => [recipeEntry, ...prev]);
      
      logger.info('Recipe search completed successfully', { 
        recipeId: recipeEntry.id, 
        query 
      });
      
      toast.success('Рецепт найден', {
        description: `${query} успешно найден через Tavily`
      });
    } catch (error: any) {
      logger.error(
        'Recipe search failed', 
        { 
          query, 
          errorMessage: error.response?.data?.detail || error.message,
          statusCode: error.response?.status,
          errorCode: error.code
        }, 
        error instanceof Error ? error : new Error(String(error))
      );
      const errorMessage = error.code === 'ECONNABORTED' || error.message?.includes('timeout')
        ? 'Таймаут подключения к серверу'
        : error.response?.data?.detail || 'Не удалось найти рецепт';
      toast.error('Ошибка поиска', {
        description: errorMessage
      });
    } finally {
      setIsSearching(false);
    }
  };

  const handleSelectRecipe = (id: string) => {
    logger.debug('Recipe selected', { recipeId: id });
    setSelectedRecipeId(id);
    setViewMode('detail');
  };

  const handleRerunRecipes = (ids: string[]) => {
    logger.info('Rerunning recipes', { recipeIds: ids, count: ids.length });
    // Simulate reprocessing
    setRecipes((prev) =>
      prev.map((r) => (ids.includes(r.id) ? { ...r, status: 'pending' as const } : r))
    );

    setTimeout(() => {
      setRecipes((prev) =>
        prev.map((r) =>
          ids.includes(r.id) ? { ...r, status: 'processed' as const } : r
        )
      );
      logger.info('Recipes rerun completed', { count: ids.length });
      toast.success('Перезапуск завершён', {
        description: `Обработано рецептов: ${ids.length}`
      });
    }, 2000);
  };

  const handleSaveFeedback = (
    recipeId: string,
    feedback: RecipeFeedback,
    recipeData: RecipeData
  ) => {
    setRecipes((prev) =>
      prev.map((r) =>
        r.id === recipeId
          ? { ...r, feedback, recipeData }
          : r
      )
    );
  };

  const handleBackToHome = () => {
    setViewMode('home');
    setSelectedRecipeId(null);
    setActiveTab('home');
  };

  const handleDeleteRecipe = async (id: string) => {
    logger.info('Deleting recipe', { recipeId: id });
    try {
      await api.deleteRecipe(id);
      setRecipes((prev) =>
        prev.map((r) =>
          r.id === id ? { ...r, status: 'deleted' as const } : r
        )
      );
      logger.info('Recipe deleted successfully', { recipeId: id });
      toast.success('Рецепт удалён', {
        description: 'Рецепт успешно удалён из списка'
      });
    } catch (error: any) {
      logger.error(
        'Failed to delete recipe', 
        { 
          recipeId: id,
          errorMessage: error.response?.data?.detail || error.message,
          statusCode: error.response?.status 
        }, 
        error instanceof Error ? error : new Error(String(error))
      );
      toast.error('Ошибка удаления', {
        description: error.response?.data?.detail || 'Не удалось удалить рецепт'
      });
    }
  };

  const selectedRecipe = recipes.find((r) => r.id === selectedRecipeId);

  const handleTabChange = (value: string) => {
    setActiveTab(value);
    if (value === 'home') {
      setViewMode('home');
    } else if (value === 'settings') {
      setViewMode('settings');
    } else if (value === 'analytics') {
      setViewMode('analytics');
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Toaster position="top-right" />
      
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center gap-3">
            <ChefHat className="w-8 h-8 text-primary" />
            <div>
              <h1 className="text-xl">Recipe Pipeline Verifier</h1>
              <p className="text-sm text-muted-foreground">
                Поиск, верификация и улучшение рецептов через LLM
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {viewMode === 'detail' && selectedRecipe ? (
          <RecipeDetailPage
            recipe={selectedRecipe}
            onBack={handleBackToHome}
            onSaveFeedback={handleSaveFeedback}
          />
        ) : (
          <Tabs value={activeTab} onValueChange={handleTabChange}>
            <TabsList className="mb-6">
              <TabsTrigger value="home" className="flex items-center gap-2">
                <Home className="w-4 h-4" />
                Главная
              </TabsTrigger>
              <TabsTrigger value="analytics" className="flex items-center gap-2">
                <BarChart3 className="w-4 h-4" />
                Аналитика
              </TabsTrigger>
              <TabsTrigger value="settings" className="flex items-center gap-2">
                <Settings className="w-4 h-4" />
                Настройки
              </TabsTrigger>
            </TabsList>

            <TabsContent value="home">
              <HomePage
                recipes={recipes}
                onSearch={handleSearch}
                onSelectRecipe={handleSelectRecipe}
                onRerunRecipes={handleRerunRecipes}
                onDeleteRecipe={handleDeleteRecipe}
                isLoading={isSearching || isLoadingRecipes}
              />
            </TabsContent>

            <TabsContent value="analytics">
              <AnalyticsDashboard
                analytics={mockAnalytics}
                promptVersions={mockPromptVersions}
              />
            </TabsContent>

            <TabsContent value="settings">
              <SettingsPanel settings={settings} onChange={setSettings} />
            </TabsContent>
          </Tabs>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t mt-12">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <p>
              © 2026 Recipe Pipeline Verifier • Powered by Tavily & OpenAI
            </p>
            <p>
              Всего рецептов: {recipes.length} • Обработано:{' '}
              {recipes.filter((r) => r.status === 'processed').length}
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
