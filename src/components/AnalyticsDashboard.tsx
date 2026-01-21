import React from 'react';
import { Download } from 'lucide-react';
import { MetricsOverview } from './MetricsOverview';
import { ErrorAnalysis } from './ErrorAnalysis';
import { Button } from './ui/button';
import { toast } from 'sonner';
import type { RecipeStatsResponse } from '../lib/api';

interface AnalyticsDashboardProps {
  stats: RecipeStatsResponse;
}

function topErrorsFromStats(stats: RecipeStatsResponse): Array<{ type: string; count: number; percentage: number }> {
  const by = stats.by_error_type || {};
  const failureTotal = stats.by_status?.failure ?? 0;
  if (failureTotal === 0) return [];
  const entries = Object.entries(by)
    .map(([type, count]) => ({
      type,
      count,
      percentage: Math.round((count / failureTotal) * 100),
    }))
    .sort((a, b) => b.count - a.count);
  return entries.slice(0, 10);
}

export function AnalyticsDashboard({ stats }: AnalyticsDashboardProps) {
  const topErrors = topErrorsFromStats(stats);

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
      <ErrorAnalysis topErrors={topErrors} />
    </div>
  );
}
