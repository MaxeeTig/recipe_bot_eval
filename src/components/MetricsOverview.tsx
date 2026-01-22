import React from 'react';
import { Hash } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { ChartContainer, ChartTooltip, ChartTooltipContent, ChartLegend, ChartLegendContent } from './ui/chart';
import { PieChart, Pie, Cell } from 'recharts';
import type { RecipeStatsResponse } from '../lib/api';

interface MetricsOverviewProps {
  stats: RecipeStatsResponse;
}

export function MetricsOverview({ stats }: MetricsOverviewProps) {
  const { total, by_status } = stats;
  const success = by_status?.success ?? 0;
  const failure = by_status?.failure ?? 0;
  const newCount = by_status?.new ?? 0;

  const chartData = [
    { 
      name: 'Успешные', 
      value: success,
    },
    { 
      name: 'С ошибками', 
      value: failure,
    },
    { 
      name: 'Новые', 
      value: newCount,
    },
  ].filter(item => item.value > 0); // Only show non-zero values

  const chartConfig = {
    Успешные: {
      label: 'Успешные',
      color: '#22c55e', // Green for success
    },
    'С ошибками': {
      label: 'С ошибками',
      color: '#ef4444', // Red for errors
    },
    Новые: {
      label: 'Новые',
      color: '#3b82f6', // Blue for new
    },
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Hash className="w-5 h-5 text-muted-foreground" />
              Статистика рецептов
            </CardTitle>
            <CardDescription>Всего: {total}</CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {total === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-8">Нет данных</p>
        ) : chartData.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-8">Нет данных для отображения</p>
        ) : (
          <div className="w-full" style={{ height: '300px' }}>
            <ChartContainer 
              config={chartConfig} 
              className="h-full w-full"
            >
              <PieChart>
                <ChartTooltip
                  content={({ active, payload }) => {
                    if (!active || !payload?.length) return null;
                    const data = payload[0];
                    const percentage = total > 0 ? Math.round(((data.value as number) / total) * 100) : 0;
                    return (
                      <ChartTooltipContent>
                        <div className="flex items-center gap-2">
                          <div
                            className="h-2 w-2 rounded-full"
                            style={{ backgroundColor: data.payload?.fill || 'currentColor' }}
                          />
                          <span className="font-medium">{data.name}</span>
                          <span className="text-muted-foreground">
                            {data.value} ({percentage}%)
                          </span>
                        </div>
                      </ChartTooltipContent>
                    );
                  }}
                />
                <Pie
                  data={chartData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  innerRadius={40}
                  label={({ value }) => value}
                  labelLine={false}
                >
                  {chartData.map((entry, index) => {
                    const colorKey = entry.name as keyof typeof chartConfig;
                    const color = chartConfig[colorKey]?.color || `hsl(var(--chart-${(index % 3) + 1}))`;
                    return (
                      <Cell key={`cell-${index}`} fill={color} />
                    );
                  })}
                </Pie>
                <ChartLegend
                  content={<ChartLegendContent nameKey="name" />}
                  className="-bottom-2"
                />
              </PieChart>
            </ChartContainer>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
