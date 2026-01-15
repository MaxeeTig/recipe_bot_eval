import React from 'react';
import { ExternalLink } from 'lucide-react';
import { RecipeSource } from '../types/recipe';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { ScrollArea } from './ui/scroll-area';

interface OriginalRecipeViewProps {
  source: RecipeSource;
  metadata: {
    date: string;
    model: string;
    promptVersion: string;
  };
}

export function OriginalRecipeView({ source, metadata }: OriginalRecipeViewProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('ru-RU', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <CardTitle className="text-lg">Оригинал из источника</CardTitle>
        <div className="flex flex-wrap gap-2 mt-2">
          <Badge variant="outline">
            Модель: {metadata.model}
          </Badge>
          <Badge variant="outline">
            Промпт: {metadata.promptVersion}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col gap-4">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Источник:</span>
            <a
              href={source.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-blue-600 hover:underline flex items-center gap-1"
            >
              {source.url}
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
          <div className="text-sm text-muted-foreground">
            Дата поиска: {formatDate(metadata.date)}
          </div>
          <div className="text-sm text-muted-foreground">
            Запрос: "{source.searchQuery}"
          </div>
        </div>

        <div className="flex-1 border rounded-md">
          <ScrollArea className="h-[500px] p-4">
            <pre className="whitespace-pre-wrap text-sm">{source.rawText}</pre>
          </ScrollArea>
        </div>
      </CardContent>
    </Card>
  );
}
