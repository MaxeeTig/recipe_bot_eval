import React, { useState, useEffect } from 'react';
import { Home, Settings, BarChart3, ChefHat } from 'lucide-react';
import { HomePage } from './components/HomePage';
import { RecipeDetailPage } from './components/RecipeDetailPage';
import { SettingsPanel } from './components/SettingsPanel';
import { AnalyticsDashboard } from './components/AnalyticsDashboard';
import type { RecipeEntry, Settings as SettingsType } from './types/recipe';
import { mockRecipes, defaultSettings } from './lib/mockData';
import { api } from './lib/api';
import type { RecipeStatsResponse } from './lib/api';
import { listItemToRecipeEntry, detailToRecipeEntry, searchResponseToRecipeEntry } from './lib/recipeTransform';
import { Tabs, TabsList, TabsTrigger, TabsContent } from './components/ui/tabs';
import { Toaster } from './components/ui/sonner';
import { toast } from 'sonner';
import { logger } from './lib/logger';
import { loadSettings, saveSettings } from './lib/storage';

type ViewMode = 'home' | 'detail' | 'settings' | 'analytics';

const EMPTY_STATS: RecipeStatsResponse = { total: 0, by_status: {}, by_error_type: {} };

export default function App() {
  const [viewMode, setViewMode] = useState<ViewMode>('home');
  const [recipes, setRecipes] = useState<RecipeEntry[]>(mockRecipes);
  const [selectedRecipeId, setSelectedRecipeId] = useState<string | null>(null);
  const [settings, setSettings] = useState<SettingsType>(() => loadSettings());
  const [isSearching, setIsSearching] = useState(false);
  const [searchProgress, setSearchProgress] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('home');
  const [isLoadingRecipes, setIsLoadingRecipes] = useState(true);
  const [isLoadingRecipeDetail, setIsLoadingRecipeDetail] = useState(false);
  const [stats, setStats] = useState<RecipeStatsResponse | null>(null);
  const [statsLoading, setStatsLoading] = useState(false);

  // Load recipes from API on mount
  useEffect(() => {
    const loadRecipes = async () => {
      try {
        setIsLoadingRecipes(true);
        logger.info('Loading recipes from API');
        const items = await api.getRecipes();
        setRecipes(items.map(listItemToRecipeEntry));
        logger.info('Recipes loaded successfully', { count: items.length });
      } catch (error: unknown) {
        const err = error instanceof Error ? error : new Error(String(error));
        logger.error('Failed to load recipes', { error }, err);
        const msg = (error as { code?: string; message?: string; response?: { data?: { detail?: string } } })?.response?.data?.detail
          || ((error as { code?: string })?.code === 'ECONNABORTED' || (error as { message?: string })?.message?.includes('timeout')
            ? 'Таймаут подключения к серверу'
            : 'Проверьте подключение к серверу');
        toast.error('Не удалось загрузить рецепты', { description: msg });
      } finally {
        setIsLoadingRecipes(false);
      }
    };
    loadRecipes();
  }, []);

  // Fetch stats when Analytics tab is selected
  useEffect(() => {
    if (activeTab !== 'analytics') return;
    let cancelled = false;
    setStatsLoading(true);
    api.getRecipeStats()
      .then((s) => { if (!cancelled) setStats(s); })
      .catch(() => { if (!cancelled) setStats(EMPTY_STATS); })
      .finally(() => { if (!cancelled) setStatsLoading(false); });
    return () => { cancelled = true; };
  }, [activeTab]);

  // Save settings to localStorage whenever they change
  useEffect(() => {
    saveSettings(settings);
  }, [settings]);

  const handleSearch = async (query: string) => {
    setIsSearching(true);
    setSearchProgress('Инициализация браузера...');
    logger.info('Recipe search initiated', { query });
    
    let isCancelled = false;
    
    // Update progress messages at different stages (based on logs: search takes ~86-89s total)
    const progressTimer1 = setTimeout(() => {
      if (!isCancelled) {
        setSearchProgress('Поиск рецепта на сайте...');
      }
    }, 10000); // 10 seconds
    
    const progressTimer2 = setTimeout(() => {
      if (!isCancelled) {
        setSearchProgress('Извлечение данных рецепта...');
      }
    }, 30000); // 30 seconds
    
    const progressTimer3 = setTimeout(() => {
      if (!isCancelled) {
        setSearchProgress('Обработка содержимого рецепта...');
      }
    }, 60000); // 60 seconds
    
    const progressTimer4 = setTimeout(() => {
      if (!isCancelled) {
        setSearchProgress('Завершение извлечения данных...');
      }
    }, 90000); // 90 seconds
    
    try {
      const res = await api.searchRecipe(query);
      if (!isCancelled) {
        setSearchProgress('Сохранение рецепта...');
      }
      const full = await api.getRecipe(String(res.recipe_id));
      const entry = detailToRecipeEntry(full);
      setRecipes((prev) => [entry, ...prev]);
      logger.info('Recipe search completed successfully', { recipeId: entry.id, query });
      toast.success('Рецепт найден', {
        description: `«${query}» найден на russianfood.com`
      });
    } catch (error: unknown) {
      const e = error as { code?: string; message?: string; response?: { data?: { detail?: string }; status?: number } };
      logger.error('Recipe search failed', { query, errorMessage: e?.response?.data?.detail || e?.message, statusCode: e?.response?.status }, error instanceof Error ? error : new Error(String(error)));
      
      // Improved error messages
      let msg: string;
      if (e?.code === 'ECONNABORTED' || e?.message?.includes('timeout')) {
        msg = 'Поиск занимает больше времени, чем ожидалось. Пожалуйста, попробуйте еще раз или проверьте подключение к интернету.';
      } else {
        msg = e?.response?.data?.detail || 'Не удалось найти рецепт';
      }
      toast.error('Ошибка поиска', { description: msg });
    } finally {
      isCancelled = true;
      clearTimeout(progressTimer1);
      clearTimeout(progressTimer2);
      clearTimeout(progressTimer3);
      clearTimeout(progressTimer4);
      setIsSearching(false);
      setSearchProgress(null);
    }
  };

  const handleSelectRecipe = async (id: string) => {
    logger.debug('Recipe selected', { recipeId: id });
    setIsLoadingRecipeDetail(true);
    try {
      let full = await api.getRecipe(id);
      if (!full.parsed_recipe && full.status !== 'failure') {
        logger.info('Recipe not parsed, triggering parse', { recipeId: id });
        toast.info('Обработка рецепта', { description: 'Парсинг рецепта через LLM...' });
        try {
          await api.parseRecipe(id, {
            model: settings.modelParsing || undefined,
            provider: settings.provider || undefined,
          });
          full = await api.getRecipe(id);
          toast.success('Рецепт обработан', { description: 'Рецепт успешно распарсен' });
        } catch (parseErr: unknown) {
          const pe = parseErr as { response?: { data?: { detail?: string } }; message?: string };
          logger.error('Failed to parse recipe', { recipeId: id, errorMessage: pe?.response?.data?.detail || pe?.message }, parseErr instanceof Error ? parseErr : new Error(String(parseErr)));
          toast.error('Ошибка обработки', { description: pe?.response?.data?.detail || 'Не удалось обработать рецепт' });
        }
      }
      const entry = detailToRecipeEntry(full);
      setRecipes((prev) => prev.map((r) => (r.id === id ? entry : r)));
      setSelectedRecipeId(id);
      setViewMode('detail');
      logger.info('Recipe detail loaded successfully', { recipeId: id });
    } catch (error: unknown) {
      const e = error as { code?: string; message?: string; response?: { data?: { detail?: string }; status?: number } };
      logger.error('Failed to load recipe detail', { recipeId: id, errorMessage: e?.response?.data?.detail || e?.message, statusCode: e?.response?.status }, error instanceof Error ? error : new Error(String(error)));
      const msg = e?.code === 'ECONNABORTED' || e?.message?.includes('timeout')
        ? 'Таймаут подключения к серверу'
        : e?.response?.data?.detail || 'Не удалось загрузить рецепт';
      toast.error('Ошибка загрузки', { description: msg });
    } finally {
      setIsLoadingRecipeDetail(false);
    }
  };

  const handleRerunRecipes = async (ids: string[]) => {
    logger.info('Rerunning recipes', { recipeIds: ids, count: ids.length });
    try {
      for (const id of ids) {
        await api.parseRecipe(id, {
          model: settings.modelParsing || undefined,
          provider: settings.provider || undefined,
        });
      }
      const items = await api.getRecipes();
      setRecipes(items.map(listItemToRecipeEntry));
      toast.success('Перезапуск завершён', { description: `Обработано рецептов: ${ids.length}` });
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } }; message?: string };
      toast.error('Ошибка перезапуска', { description: e?.response?.data?.detail || e?.message || 'Ошибка' });
    }
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
      setRecipes((prev) => prev.filter((r) => r.id !== id));
      if (selectedRecipeId === id) {
        setSelectedRecipeId(null);
        setViewMode('home');
        setActiveTab('home');
      }
      toast.success('Рецепт удалён', { description: 'Рецепт удалён из списка' });
    } catch (error: unknown) {
      const e = error as { response?: { data?: { detail?: string } }; message?: string };
      toast.error('Ошибка удаления', { description: e?.response?.data?.detail || 'Не удалось удалить рецепт' });
    }
  };

  const handleRecipeUpdated = (entry: RecipeEntry) => {
    setRecipes((prev) => prev.map((r) => (r.id === entry.id ? entry : r)));
    setSelectedRecipeId(entry.id);
  };

  const selectedRecipe = recipes.find((r) => r.id === selectedRecipeId);

  const handleTabChange = (value: string) => {
    setActiveTab(value);
    if (value === 'home') setViewMode('home');
    else if (value === 'settings') setViewMode('settings');
    else if (value === 'analytics') setViewMode('analytics');
  };

  return (
    <div className="min-h-screen bg-background">
      <Toaster position="top-right" />

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

      <main className="container mx-auto px-6 py-8">
        {viewMode === 'detail' && selectedRecipe ? (
          <RecipeDetailPage
            recipe={selectedRecipe}
            onBack={handleBackToHome}
            onRecipeUpdated={handleRecipeUpdated}
            modelAnalysis={settings.modelAnalysis}
            provider={settings.provider}
            isLoading={isLoadingRecipeDetail}
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
                searchProgress={searchProgress}
              />
            </TabsContent>

            <TabsContent value="analytics">
              {statsLoading ? (
                <p className="text-muted-foreground">Загрузка статистики...</p>
              ) : (
                <AnalyticsDashboard stats={stats || EMPTY_STATS} />
              )}
            </TabsContent>

            <TabsContent value="settings">
              <SettingsPanel settings={settings} onChange={setSettings} />
            </TabsContent>
          </Tabs>
        )}
      </main>

      <footer className="border-t mt-12">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <p>© 2026 Recipe Pipeline Verifier • russianfood.com & LLM</p>
            <p>
              Всего рецептов: {recipes.length} • Обработано: {recipes.filter((r) => r.status === 'processed').length}
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
