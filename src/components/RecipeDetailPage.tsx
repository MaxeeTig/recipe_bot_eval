import React, { useState, useEffect } from 'react';
import { ArrowLeft, Loader2, AlertCircle, FileCode, RefreshCw, CheckCircle2 } from 'lucide-react';
import type { RecipeEntry, RecipeData } from '../types/recipe';
import { OriginalRecipeView } from './OriginalRecipeView';
import { StructuredRecipeView } from './StructuredRecipeView';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
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
  const [applyPatchesRunning, setApplyPatchesRunning] = useState(false);
  const [reparseRunning, setReparseRunning] = useState(false);
  const [latestAnalysis, setLatestAnalysis] = useState<AnalysisResponse | null>(null);
  const [patchesApplied, setPatchesApplied] = useState(false);

  useEffect(() => {
    if (recipe.recipeData) setRecipeData(recipe.recipeData);
  }, [recipe.recipeData]);

  useEffect(() => {
    if (recipe.status !== 'error') return;
    let cancelled = false;
    setAnalysesLoading(true);
    api.getRecipeAnalyses(recipe.id)
      .then((list) => { 
        if (!cancelled) {
          setAnalyses(list);
          // Set latest analysis if available
          if (list.length > 0) {
            setLatestAnalysis(list[0]);
            // Check if patches were already applied (via reparse success)
            const hasSuccessfulReparse = list.some(a => a.reparse_result?.status === 'success');
            setPatchesApplied(hasSuccessfulReparse);
          }
        }
      })
      .finally(() => { if (!cancelled) setAnalysesLoading(false); });
    return () => { cancelled = true; };
  }, [recipe.id, recipe.status]);

  // Get patches from analysis report
  const getPatchesFromAnalysis = (analysis: AnalysisResponse): Record<string, unknown> | null => {
    const report = analysis.analysis_report || {};
    const patches = report.patches;
    if (!patches || typeof patches !== 'object') return null;
    return patches as Record<string, unknown>;
  };

  // Check if analysis has patches
  const hasPatches = (analysis: AnalysisResponse | null): boolean => {
    if (!analysis) return false;
    const patches = getPatchesFromAnalysis(analysis);
    if (!patches) return false;
    return !!(patches.unit_mapping || patches.cleanup_rules || patches.system_prompt_append);
  };

  // Render patches preview
  const renderPatchesPreview = (analysis: AnalysisResponse) => {
    const patches = getPatchesFromAnalysis(analysis);
    if (!patches) return null;

    return (
      <div className="mt-4 p-3 bg-muted rounded-lg space-y-2 text-sm">
        <p className="font-semibold text-xs text-muted-foreground uppercase">Патчи для применения:</p>
        {patches.unit_mapping && typeof patches.unit_mapping === 'object' && Object.keys(patches.unit_mapping).length > 0 && (
          <div>
            <Badge variant="outline" className="mr-2">unit_mapping</Badge>
            <span className="text-xs text-muted-foreground">
              {Object.keys(patches.unit_mapping).length} единиц измерения
            </span>
          </div>
        )}
        {patches.cleanup_rules && Array.isArray(patches.cleanup_rules) && patches.cleanup_rules.length > 0 && (
          <div>
            <Badge variant="outline" className="mr-2">cleanup_rules</Badge>
            <span className="text-xs text-muted-foreground">
              {patches.cleanup_rules.length} правил очистки
            </span>
          </div>
        )}
        {patches.system_prompt_append && typeof patches.system_prompt_append === 'string' && (
          <div>
            <Badge variant="outline" className="mr-2">system_prompt_append</Badge>
            <span className="text-xs text-muted-foreground">
              Дополнение к системному промпту
            </span>
          </div>
        )}
      </div>
    );
  };

  // Step 1: Analyze error
  const handleAnalyze = async () => {
    setAnalyzeRunning(true);
    try {
      // Just analyze, no patches, no reparse
      const res = await api.analyzeRecipe(recipe.id, {
        model: modelAnalysis || undefined,
        provider: provider || undefined,
        apply_patches: false,
        reparse: false,
      });
      const list = await api.getRecipeAnalyses(recipe.id);
      setAnalyses(list);
      setLatestAnalysis(res);
      setPatchesApplied(false); // Reset patches applied state
      toast.success('Анализ выполнен', { description: res.recommendations_summary || 'Отчёт сохранён' });
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } }; message?: string };
      toast.error('Ошибка анализа', { description: e?.response?.data?.detail || e?.message || 'Ошибка' });
    } finally {
      setAnalyzeRunning(false);
    }
  };

  // Step 2: Apply patches
  const handleApplyPatches = async () => {
    if (!latestAnalysis) return;
    setApplyPatchesRunning(true);
    try {
      // Apply patches from latest analysis using the new endpoint
      await api.applyPatchesFromAnalysis(recipe.id, latestAnalysis.analysis_id);
      setPatchesApplied(true);
      toast.success('Патчи применены', { description: 'Патчи сохранены в папку patches/' });
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } }; message?: string };
      toast.error('Ошибка применения патчей', { description: e?.response?.data?.detail || e?.message || 'Ошибка' });
    } finally {
      setApplyPatchesRunning(false);
    }
  };

  // Step 3: Re-parse recipe
  const handleReparse = async () => {
    setReparseRunning(true);
    try {
      // Re-parse using standard parsing (patches will be automatically used)
      const parseResult = await api.parseRecipe(recipe.id, {
        model: modelAnalysis || undefined,
        provider: provider || undefined,
      });
      
      // Check the parse response status directly
      if (parseResult.status === 'success') {
        // Get updated recipe data
        const full = await api.getRecipe(recipe.id);
        const entry = detailToRecipeEntry(full);
        onRecipeUpdated(entry);
        toast.success('Рецепт успешно распарсен', { description: 'Парсинг завершён с применёнными патчами' });
      } else {
        // Parse failed - get updated recipe to show error
        const full = await api.getRecipe(recipe.id);
        const entry = detailToRecipeEntry(full);
        onRecipeUpdated(entry);
        const errorMsg = parseResult.error?.message || 'Парсинг не удался даже с патчами';
        toast.error('Ошибка парсинга', { description: errorMsg });
      }
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } }; message?: string };
      toast.error('Ошибка парсинга', { description: e?.response?.data?.detail || e?.message || 'Ошибка' });
    } finally {
      setReparseRunning(false);
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

                {/* Step 1: Analyze Error */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <span className="flex items-center justify-center w-6 h-6 rounded-full bg-primary text-primary-foreground text-xs font-bold">1</span>
                      Анализ ошибки
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="text-sm text-muted-foreground">
                      Запустите анализ, чтобы определить причину ошибки и получить рекомендации по исправлению.
                    </p>
                    <Button 
                      onClick={handleAnalyze} 
                      disabled={analyzeRunning}
                      className="w-full"
                    >
                      {analyzeRunning ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin mr-2" />
                          Анализ...
                        </>
                      ) : (
                        <>
                          <FileCode className="w-4 h-4 mr-2" />
                          Анализировать ошибку
                        </>
                      )}
                    </Button>
                    {latestAnalysis && (
                      <div className="mt-4 p-4 bg-muted rounded-lg space-y-3">
                        <div className="flex items-start gap-2">
                          <CheckCircle2 className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-semibold">Анализ завершён</p>
                            <p className="text-xs text-muted-foreground mt-1">
                              {latestAnalysis.created_at}
                            </p>
                            {latestAnalysis.recommendations_summary && (
                              <p className="text-sm mt-2">{latestAnalysis.recommendations_summary}</p>
                            )}
                            {renderPatchesPreview(latestAnalysis)}
                          </div>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Step 2: Apply Patches */}
                {latestAnalysis && hasPatches(latestAnalysis) && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <span className="flex items-center justify-center w-6 h-6 rounded-full bg-primary text-primary-foreground text-xs font-bold">2</span>
                        Применить патчи
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <p className="text-sm text-muted-foreground">
                        Примените рекомендованные патчи из анализа. Они будут сохранены в папку patches/ и использованы при следующем парсинге.
                      </p>
                      {renderPatchesPreview(latestAnalysis)}
                      <Button 
                        onClick={handleApplyPatches} 
                        disabled={applyPatchesRunning || patchesApplied}
                        variant={patchesApplied ? "secondary" : "default"}
                        className="w-full"
                      >
                        {applyPatchesRunning ? (
                          <>
                            <Loader2 className="w-4 h-4 animate-spin mr-2" />
                            Применение...
                          </>
                        ) : patchesApplied ? (
                          <>
                            <CheckCircle2 className="w-4 h-4 mr-2" />
                            Патчи применены
                          </>
                        ) : (
                          <>
                            <FileCode className="w-4 h-4 mr-2" />
                            Применить патчи
                          </>
                        )}
                      </Button>
                    </CardContent>
                  </Card>
                )}

                {/* Step 3: Re-parse Recipe */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <span className="flex items-center justify-center w-6 h-6 rounded-full bg-primary text-primary-foreground text-xs font-bold">3</span>
                      Перепарсить рецепт
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="text-sm text-muted-foreground">
                      После применения патчей перепарсите рецепт. Если патчи были применены, парсинг должен пройти успешно.
                    </p>
                    <Button 
                      onClick={handleReparse} 
                      disabled={reparseRunning || !latestAnalysis}
                      className="w-full"
                    >
                      {reparseRunning ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin mr-2" />
                          Парсинг...
                        </>
                      ) : (
                        <>
                          <RefreshCw className="w-4 h-4 mr-2" />
                          Перепарсить рецепт
                        </>
                      )}
                    </Button>
                  </CardContent>
                </Card>

                {/* Analysis History */}
                <Card>
                  <CardHeader>
                    <CardTitle>История анализов</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {analysesLoading ? (
                      <p className="text-sm text-muted-foreground">Загрузка...</p>
                    ) : analyses.length === 0 ? (
                      <p className="text-sm text-muted-foreground">Пока нет анализов. Запустите анализ выше.</p>
                    ) : (
                      <ul className="space-y-3 text-sm">
                        {analyses.map((a) => (
                          <li key={a.analysis_id} className="border-b pb-3 last:border-0">
                            <div className="flex items-start justify-between gap-2">
                              <span className="text-muted-foreground text-xs">{a.created_at}</span>
                              {a.analysis_id === latestAnalysis?.analysis_id && (
                                <Badge variant="outline" className="text-xs">Текущий</Badge>
                              )}
                            </div>
                            <p className="mt-1">{a.recommendations_summary || 'Анализ без описания'}</p>
                            {hasPatches(a) && (
                              <div className="mt-2">
                                {renderPatchesPreview(a)}
                              </div>
                            )}
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
