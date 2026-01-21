import React from 'react';
import { Hash, AlertCircle, CheckCircle2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import type { RecipeStatsResponse } from '../lib/api';

interface MetricsOverviewProps {
  stats: RecipeStatsResponse;
}

export function MetricsOverview({ stats }: MetricsOverviewProps) {
  const { total, by_status } = stats;
  const withErrors = by_status?.failure ?? 0;
  const withoutErrors = (by_status?.success ?? 0) + (by_status?.new ?? 0);
  const successRate = total > 0 ? Math.round(((by_status?.success ?? 0) / total) * 100) : 0;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <Card>
        <CardHeader className="pb-2">
          <CardDescription>Всего рецептов</CardDescription>
          <CardTitle className="flex items-center gap-2">
            <Hash className="w-5 h-5 text-muted-foreground" />
            {total}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-xs text-muted-foreground">
            new: {by_status?.new ?? 0} · success: {by_status?.success ?? 0} · failure: {withErrors}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardDescription>С ошибками</CardDescription>
          <CardTitle className="flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-red-600" />
            {withErrors}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-xs text-muted-foreground">
            {total > 0 ? Math.round((withErrors / total) * 100) : 0}% от всего
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardDescription>Без ошибок</CardDescription>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-green-600" />
            {withoutErrors}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-xs text-muted-foreground">
            Успешных: {by_status?.success ?? 0} · Ожидают: {by_status?.new ?? 0} ({successRate}% success)
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
