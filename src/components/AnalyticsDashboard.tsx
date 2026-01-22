import React from 'react';
import { Download, CheckCircle2 } from 'lucide-react';
import { MetricsOverview } from './MetricsOverview';
import { ErrorAnalysis } from './ErrorAnalysis';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { toast } from 'sonner';
import type { RecipeStatsResponse } from '../lib/api';

interface AnalyticsDashboardProps {
  stats: RecipeStatsResponse;
}

function topPatchTypesFromStats(stats: RecipeStatsResponse): Array<{ type: string; count: number; percentage: number }> {
  const by = stats.by_patch_type || {};
  const totalPatches = Object.values(by).reduce((sum, count) => sum + count, 0);
  if (totalPatches === 0) return [];
  
  // Map patch type keys to readable labels
  const patchTypeLabels: Record<string, string> = {
    'unit_mapping': 'Маппинг единиц',
    'cleanup_rules': 'Правила очистки',
    'system_prompt_append': 'Дополнение промпта'
  };
  
  const entries = Object.entries(by)
    .filter(([_, count]) => count > 0)
    .map(([type, count]) => ({
      type: patchTypeLabels[type] || type,
      count,
      percentage: Math.round((count / totalPatches) * 100),
    }))
    .sort((a, b) => b.count - a.count);
  return entries;
}

export function AnalyticsDashboard({ stats }: AnalyticsDashboardProps) {
  const topPatchTypes = topPatchTypesFromStats(stats);

  const handleExportData = () => {
    const data = { stats, exportDate: new Date().toISOString() };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `recipe-stats-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success('Данные экспортированы', {
      description: 'JSON файл загружен на ваше устройство',
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1>Аналитика</h1>
          <p className="text-muted-foreground">
            Статистика рецептов: всего, с ошибками и без
          </p>
        </div>
        <Button onClick={handleExportData} variant="outline">
          <Download className="w-4 h-4 mr-2" />
          Экспорт
        </Button>
      </div>

      <MetricsOverview stats={stats} />
      
      {stats.corrections_count !== null && stats.corrections_count !== undefined && (
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-green-600" />
              <CardTitle>Успешные исправления</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold">{stats.corrections_count}</span>
              <CardDescription>
                рецептов успешно исправлено после применения патчей
              </CardDescription>
            </div>
          </CardContent>
        </Card>
      )}

      <ErrorAnalysis topPatchTypes={topPatchTypes} />
    </div>
  );
}
