import React, { useState } from 'react';
import { BarChart3, Sparkles, Download } from 'lucide-react';
import { MetricsOverview } from './MetricsOverview';
import { ErrorAnalysis } from './ErrorAnalysis';
import { PromptVersionHistory } from './PromptVersionHistory';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { toast } from 'sonner';

interface AnalyticsDashboardProps {
  analytics: {
    successRate: number;
    averageScores: {
      ingredientAccuracy: number;
      dataCompleteness: number;
      originalMatch: number;
      overallQuality: number;
    };
    topErrors: Array<{
      type: string;
      count: number;
      percentage: number;
    }>;
    totalRecipes: number;
    processedRecipes: number;
    readyForProduction: number;
  };
  promptVersions: Array<{
    version: string;
    date: string;
    changes: string;
    effectOnMetrics: string;
  }>;
}

export function AnalyticsDashboard({ analytics, promptVersions }: AnalyticsDashboardProps) {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  const handleAnalyzeErrors = () => {
    setIsAnalyzing(true);
    setTimeout(() => {
      setIsAnalyzing(false);
      toast.success('Анализ завершён', {
        description: 'Обнаружено 3 основных паттерна ошибок'
      });
    }, 2000);
  };

  const handleGenerateImprovements = () => {
    setIsGenerating(true);
    setTimeout(() => {
      setIsGenerating(false);
      toast.success('Улучшения сгенерированы', {
        description: 'Предложения по оптимизации промпта готовы'
      });
    }, 3000);
  };

  const handleExportData = () => {
    const data = {
      analytics,
      promptVersions,
      exportDate: new Date().toISOString()
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `recipe-analytics-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success('Данные экспортированы', {
      description: 'JSON файл загружен на ваше устройство'
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1>Аналитика и улучшения</h1>
          <p className="text-muted-foreground">
            Мониторинг качества пайплайна и генерация улучшений
          </p>
        </div>
        <Button onClick={handleExportData} variant="outline">
          <Download className="w-4 h-4 mr-2" />
          Экспорт данных
        </Button>
      </div>

      <MetricsOverview
        successRate={analytics.successRate}
        averageScores={analytics.averageScores}
        totalRecipes={analytics.totalRecipes}
        processedRecipes={analytics.processedRecipes}
        readyForProduction={analytics.readyForProduction}
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ErrorAnalysis topErrors={analytics.topErrors} />

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-purple-600" />
              Действия
            </CardTitle>
            <CardDescription>
              Автоматический анализ и улучшение системы
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button
              onClick={handleAnalyzeErrors}
              disabled={isAnalyzing}
              className="w-full"
              variant="outline"
            >
              {isAnalyzing ? 'Анализируем...' : 'Запустить анализ ошибок'}
            </Button>
            <Button
              onClick={handleGenerateImprovements}
              disabled={isGenerating}
              className="w-full bg-purple-600 hover:bg-purple-700"
            >
              <Sparkles className="w-4 h-4 mr-2" />
              {isGenerating ? 'Генерируем...' : 'Сгенерировать улучшения'}
            </Button>
            <p className="text-xs text-muted-foreground">
              Система агрегирует ошибки и использует LLM для генерации предложений по улучшению промпта
            </p>
          </CardContent>
        </Card>
      </div>

      <PromptVersionHistory versions={promptVersions} />
    </div>
  );
}
