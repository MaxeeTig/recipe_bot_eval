import React from 'react';
import { AlertCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Progress } from './ui/progress';

interface ErrorAnalysisProps {
  topErrors: Array<{
    type: string;
    count: number;
    percentage: number;
  }>;
}

export function ErrorAnalysis({ topErrors }: ErrorAnalysisProps) {
  const getColorByPercentage = (percentage: number) => {
    if (percentage >= 30) return 'bg-red-500';
    if (percentage >= 20) return 'bg-orange-500';
    return 'bg-yellow-500';
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-orange-600" />
          <CardTitle>Топ-3 типа ошибок</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {topErrors.map((error, index) => (
            <div key={error.type} className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-muted-foreground">
                    #{index + 1}
                  </span>
                  <span className="font-medium">{error.type}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground">
                    {error.count} случаев
                  </span>
                  <span className="font-medium">{error.percentage}%</span>
                </div>
              </div>
              <div className="relative">
                <Progress value={error.percentage} className="h-2" />
                <div
                  className={`absolute top-0 left-0 h-2 rounded-full ${getColorByPercentage(
                    error.percentage
                  )} transition-all`}
                  style={{ width: `${error.percentage}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
