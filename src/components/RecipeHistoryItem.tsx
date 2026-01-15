import React from 'react';
import { CheckCircle2, Clock, AlertCircle, Trash2 } from 'lucide-react';
import { RecipeEntry } from '../types/recipe';
import { Checkbox } from './ui/checkbox';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from './ui/alert-dialog';

interface RecipeHistoryItemProps {
  recipe: RecipeEntry;
  isSelected: boolean;
  onSelect: (id: string, checked: boolean) => void;
  onView: (id: string) => void;
  onDelete: (id: string) => void;
}

export function RecipeHistoryItem({ recipe, isSelected, onSelect, onView, onDelete }: RecipeHistoryItemProps) {
  const statusIcons = {
    processed: <CheckCircle2 className="w-4 h-4 text-green-600" />,
    pending: <Clock className="w-4 h-4 text-yellow-600" />,
    error: <AlertCircle className="w-4 h-4 text-red-600" />,
    deleted: <AlertCircle className="w-4 h-4 text-gray-600" />
  };

  const statusLabels = {
    processed: 'Обработан',
    pending: 'Ожидает проверки',
    error: 'Ошибка',
    deleted: 'Удалён'
  };

  const statusColors = {
    processed: 'bg-green-100 text-green-800',
    pending: 'bg-yellow-100 text-yellow-800',
    error: 'bg-red-100 text-red-800',
    deleted: 'bg-gray-100 text-gray-800'
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('ru-RU', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  return (
    <div className="flex items-center gap-3 p-4 border rounded-lg hover:bg-muted/50 transition-colors">
      <Checkbox
        checked={isSelected}
        onCheckedChange={(checked) => onSelect(recipe.id, checked as boolean)}
        className="mt-1"
      />
      
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          {statusIcons[recipe.status]}
          <button
            onClick={() => recipe.status === 'processed' && onView(recipe.id)}
            className="hover:underline text-left truncate"
            disabled={recipe.status !== 'processed'}
          >
            <span className={recipe.status === 'processed' ? 'cursor-pointer' : 'cursor-default'}>
              {recipe.dishName}
            </span>
          </button>
        </div>
        
        <div className="flex items-center gap-3 text-sm text-muted-foreground">
          <span className="truncate">{recipe.query}</span>
          <span className="shrink-0">{formatDate(recipe.date)}</span>
        </div>
      </div>
      
      <Badge className={statusColors[recipe.status]} variant="secondary">
        {statusLabels[recipe.status]}
      </Badge>
      
      {recipe.status !== 'deleted' && (
        <AlertDialog>
          <AlertDialogTrigger asChild>
            <Button
              variant="ghost"
              size="sm"
              className="text-red-600 hover:text-red-700 hover:bg-red-50"
              onClick={(e) => e.stopPropagation()}
            >
              <Trash2 className="w-4 h-4" />
            </Button>
          </AlertDialogTrigger>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Удалить рецепт?</AlertDialogTitle>
              <AlertDialogDescription>
                Вы уверены, что хотите удалить рецепт "{recipe.dishName}"? Это действие нельзя отменить.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Отмена</AlertDialogCancel>
              <AlertDialogAction
                onClick={() => onDelete(recipe.id)}
                className="bg-red-600 hover:bg-red-700"
              >
                Удалить
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      )}
    </div>
  );
}
