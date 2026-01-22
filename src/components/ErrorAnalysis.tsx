import React from 'react';
import { Wrench } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Progress } from './ui/progress';

interface ErrorAnalysisProps {
  topPatchTypes: Array<{
    type: string;
    count: number;
    percentage: number;
  }>;
}

export function ErrorAnalysis({ topPatchTypes }: ErrorAnalysisProps) {
  const getColorByPercentage = (percentage: number) => {
    if (percentage >= 50) return 'bg-blue-500';
    if (percentage >= 30) return 'bg-indigo-500';
    return 'bg-purple-500';
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <Wrench className="w-5 h-5 text-blue-600" />
          <CardTitle>Типы патчей</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {topPatchTypes.length === 0 ? (
            <p className="text-sm text-muted-foreground">Нет данных по типам патчей</p>
          ) : (
          topPatchTypes.map((patchType, index) => (
            <div key={patchType.type} className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-muted-foreground">
                    #{index + 1}
                  </span>
                  <span className="font-medium">{patchType.type}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground">
                    {patchType.count} патчей
                  </span>
                  <span className="font-medium">{patchType.percentage}%</span>
                </div>
              </div>
              <div className="relative">
                <Progress value={patchType.percentage} className="h-2" />
                <div
                  className={`absolute top-0 left-0 h-2 rounded-full ${getColorByPercentage(
                    patchType.percentage
                  )} transition-all`}
                  style={{ width: `${patchType.percentage}%` }}
                />
              </div>
            </div>
          )))}
        </div>
      </CardContent>
    </Card>
  );
}
