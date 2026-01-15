import React from 'react';
import { Clock, TrendingUp } from 'lucide-react';
import { PromptVersion } from '../types/recipe';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from './ui/table';

interface PromptVersionHistoryProps {
  versions: PromptVersion[];
}

export function PromptVersionHistory({ versions }: PromptVersionHistoryProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('ru-RU', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    }).format(date);
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <Clock className="w-5 h-5 text-blue-600" />
          <CardTitle>История версий промпта</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <div className="border rounded-md">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Версия</TableHead>
                <TableHead>Дата</TableHead>
                <TableHead>Изменения</TableHead>
                <TableHead>Эффект на метрики</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {versions.map((version, index) => (
                <TableRow key={version.version}>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Badge variant={index === 0 ? 'default' : 'secondary'}>
                        {version.version}
                      </Badge>
                      {index === 0 && (
                        <span className="text-xs text-green-600">Текущая</span>
                      )}
                    </div>
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {formatDate(version.date)}
                  </TableCell>
                  <TableCell>{version.changes}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1">
                      {version.effectOnMetrics !== 'Baseline' && (
                        <TrendingUp className="w-4 h-4 text-green-600" />
                      )}
                      <span
                        className={
                          version.effectOnMetrics !== 'Baseline'
                            ? 'text-green-600 font-medium'
                            : 'text-muted-foreground'
                        }
                      >
                        {version.effectOnMetrics}
                      </span>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
