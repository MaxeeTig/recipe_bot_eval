import React from 'react';
import { TrendingUp, CheckCircle2, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Progress } from './ui/progress';

interface MetricsOverviewProps {
  successRate: number;
  averageScores: {
    ingredientAccuracy: number;
    dataCompleteness: number;
    originalMatch: number;
    overallQuality: number;
  };
  totalRecipes: number;
  processedRecipes: number;
  readyForProduction: number;
}

export function MetricsOverview({
  successRate,
  averageScores,
  totalRecipes,
  processedRecipes,
  readyForProduction
}: MetricsOverviewProps) {
  const metrics = [
    {
      label: 'Точность ингредиентов',
      value: averageScores.ingredientAccuracy,
      color: 'bg-blue-500'
    },
    {
      label: 'Полнота данных',
      value: averageScores.dataCompleteness,
      color: 'bg-green-500'
    },
    {
      label: 'Соответствие оригиналу',
      value: averageScores.originalMatch,
      color: 'bg-purple-500'
    },
    {
      label: 'Общее качество',
      value: averageScores.overallQuality,
      color: 'bg-orange-500'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* Success Rate */}
      <Card>
        <CardHeader className="pb-2">
          <CardDescription>Успешных валидаций</CardDescription>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-green-600" />
            {successRate}%
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Progress value={successRate} className="h-2" />
          <p className="text-xs text-muted-foreground mt-2">
            {processedRecipes} из {totalRecipes} обработано
          </p>
        </CardContent>
      </Card>

      {/* Production Ready */}
      <Card>
        <CardHeader className="pb-2">
          <CardDescription>Готовы к продакшену</CardDescription>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-green-600" />
            {readyForProduction}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Progress
            value={(readyForProduction / processedRecipes) * 100}
            className="h-2"
          />
          <p className="text-xs text-muted-foreground mt-2">
            {Math.round((readyForProduction / processedRecipes) * 100)}% от обработанных
          </p>
        </CardContent>
      </Card>

      {/* Average Scores */}
      {metrics.slice(0, 2).map((metric) => (
        <Card key={metric.label}>
          <CardHeader className="pb-2">
            <CardDescription>{metric.label}</CardDescription>
            <CardTitle className="flex items-center gap-2">
              {metric.value.toFixed(1)} / 5
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Progress value={(metric.value / 5) * 100} className="h-2" />
            <div className="flex gap-1 mt-2">
              {[1, 2, 3, 4, 5].map((star) => (
                <div
                  key={star}
                  className={`w-4 h-4 rounded-sm ${
                    star <= Math.round(metric.value)
                      ? metric.color
                      : 'bg-gray-200'
                  }`}
                />
              ))}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
