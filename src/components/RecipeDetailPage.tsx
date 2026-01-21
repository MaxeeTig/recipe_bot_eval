import React, { useState, useEffect } from 'react';
import { ArrowLeft, Loader2, AlertCircle, Play } from 'lucide-react';
import type { RecipeEntry, RecipeData } from '../types/recipe';
import { OriginalRecipeView } from './OriginalRecipeView';
import { StructuredRecipeView } from './StructuredRecipeView';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Checkbox } from './ui/checkbox';
import { Label } from './ui/label';
import { toast } from 'sonner';
import { api } from '../lib/api';
import type { AnalysisResponse } from '../lib/api';
import { detailToRecipeEntry } from '../lib/recipeTransform';

interface RecipeDetailPageProps {
  recipe: RecipeEntry;
  onBack: () => void;
  onRecipeUpdated: (entry: RecipeEntry) => void;
  modelAnalysis: string;
  provider: string;
  isLoading?: boolean;
}

export function RecipeDetailPage({
  recipe,
  onBack,
  onRecipeUpdated,
  modelAnalysis,
  provider,
  isLoading = false,
}: RecipeDetailPageProps) {
  const [recipeData, setRecipeData] = useState<RecipeData | undefined>(recipe.recipeData);
  const [analyses, setAnalyses] = useState<AnalysisResponse[]>([]);
  const [analysesLoading, setAnalysesLoading] = useState(false);
  const [analyzeRunning, setAnalyzeRunning] = useState(false);
  const [applyPatches, setApplyPatches] = useState(false);
  const [reparse, setReparse] = useState(false);

  useEffect(() => {
    if (recipe.recipeData) setRecipeData(recipe.recipeData);
  }, [recipe.recipeData]);

  useEffect(() => {
    if (recipe.status !== 'error') return;
    let cancelled = false;
    setAnalysesLoading(true);
    api.getRecipeAnalyses(recipe.id)
      .then((list) => { if (!cancelled) setAnalyses(list); })
      .finally(() => { if (!cancelled) setAnalysesLoading(false); });
    return () => { cancelled = true; };
  }, [recipe.id, recipe.status]);

  const handleAnalyze = async () => {
    setAnalyzeRunning(true);
    try {
      const res = await api.analyzeRecipe(recipe.id, {
        model: modelAnalysis || undefined,
        provider: provider || undefined,
        apply_patches: applyPatches,
        reparse,
      });
      const list = await api.getRecipeAnalyses(recipe.id);
      setAnalyses(list);
      toast.success('Анализ выполнен', { description: res.recommendations_summary || 'Отчёт сохранён' });
      if (reparse && res.reparse_result?.status === 'success') {
        const full = await api.getRecipe(recipe.id);
        onRecipeUpdated(detailToRecipeEntry(full));
      }
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } }; message?: string };
      toast.error('Ошибка анализа', { description: e?.response?.data?.detail || e?.message || 'Ошибка' });
    } finally {
      setAnalyzeRunning(false);
    }
  };

  if (isLoading || !recipe.source) {
    return (
      <div className="space-y-4">
        <Button onClick={onBack} variant="ghost" size="sm">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Назад к списку
        </Button>
        <div className="text-center py-12">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-muted-foreground" />
          <p className="text-muted-foreground">
            {isLoading ? 'Загрузка данных рецепта...' : 'Данные рецепта не найдены'}
          </p>
        </div>
      </div>
    );
  }

  if (!recipeData) {
    const isError = recipe.status === 'error';
    return (
      <div className="space-y-4">
        <Button onClick={onBack} variant="ghost" size="sm">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Назад к списку
        </Button>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="space-y-6">
            <OriginalRecipeView
              source={recipe.source}
              metadata={{ date: recipe.date, model: '—', promptVersion: '—' }}
            />
          </div>
          <div className="space-y-6">
            {isError ? (
              <>
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-destructive">
                      <AlertCircle className="w-5 h-5" />
                      Ошибка парсинга
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    {recipe.error && (
                      <>
                        <p><strong>{recipe.error.type}</strong>: {recipe.error.message}</p>
                      </>
                    )}
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader>
                    <CardTitle>Запустить анализ ошибки</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-center gap-2">
                      <Checkbox id="ap" checked={applyPatches} onCheckedChange={(c) => setApplyPatches(!!c)} />
                      <Label htmlFor="ap">Применить патчи из отчёта</Label>
                    </div>
                    <div className="flex items-center gap-2">
                      <Checkbox id="rep" checked={reparse} onCheckedChange={(c) => setReparse(!!c)} />
                      <Label htmlFor="rep">Перепарсить после анализа</Label>
                    </div>
                    <Button onClick={handleAnalyze} disabled={analyzeRunning}>
                      {analyzeRunning ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Play className="w-4 h-4 mr-2" />}
                      {analyzeRunning ? 'Анализ...' : 'Запустить анализ ошибки'}
                    </Button>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader>
                    <CardTitle>Анализы</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {analysesLoading ? (
                      <p className="text-sm text-muted-foreground">Загрузка...</p>
                    ) : analyses.length === 0 ? (
                      <p className="text-sm text-muted-foreground">Пока нет анализов. Запустите анализ выше.</p>
                    ) : (
                      <ul className="space-y-3 text-sm">
                        {analyses.map((a) => (
                          <li key={a.analysis_id} className="border-b pb-2 last:border-0">
                            <span className="text-muted-foreground">{a.created_at}</span>
                            <p className="mt-1">{a.recommendations_summary || JSON.stringify(a.analysis_report).slice(0, 200)}</p>
                          </li>
                        ))}
                      </ul>
                    )}
                  </CardContent>
                </Card>
              </>
            ) : (
              <div className="border rounded-lg p-6">
                <div className="flex items-center gap-3 mb-4">
                  <Loader2 className="w-5 h-5 animate-spin text-muted-foreground" />
                </div>
                <p className="text-sm text-muted-foreground">Обработка рецепта через LLM...</p>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <Button onClick={onBack} variant="ghost" size="sm">
        <ArrowLeft className="w-4 h-4 mr-2" />
        Назад к списку
      </Button>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-6">
          <OriginalRecipeView
            source={recipe.source!}
            metadata={{
              date: recipeData.searchDate,
              model: recipeData.modelUsed,
              promptVersion: recipeData.promptVersion,
            }}
          />
        </div>
        <div className="space-y-6">
          <StructuredRecipeView recipeData={recipeData} onChange={setRecipeData} />
        </div>
      </div>
    </div>
  );
}
