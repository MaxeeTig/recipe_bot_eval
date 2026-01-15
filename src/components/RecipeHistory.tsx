import React, { useState } from 'react';
import { RefreshCw } from 'lucide-react';
import { RecipeEntry } from '../types/recipe';
import { RecipeHistoryItem } from './RecipeHistoryItem';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';

interface RecipeHistoryProps {
  recipes: RecipeEntry[];
  onSelectRecipe: (id: string) => void;
  onRerunRecipes: (ids: string[]) => void;
  onDeleteRecipe: (id: string) => void;
}

export function RecipeHistory({ recipes, onSelectRecipe, onRerunRecipes, onDeleteRecipe }: RecipeHistoryProps) {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  const handleSelect = (id: string, checked: boolean) => {
    setSelectedIds(prev => {
      const newSet = new Set(prev);
      if (checked) {
        newSet.add(id);
      } else {
        newSet.delete(id);
      }
      return newSet;
    });
  };

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedIds(new Set(recipes.map(r => r.id)));
    } else {
      setSelectedIds(new Set());
    }
  };

  const handleRerun = () => {
    if (selectedIds.size > 0) {
      onRerunRecipes(Array.from(selectedIds));
      setSelectedIds(new Set());
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>История запросов</CardTitle>
          <div className="flex items-center gap-2">
            <label className="text-sm text-muted-foreground flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={selectedIds.size === recipes.length && recipes.length > 0}
                onChange={(e) => handleSelectAll(e.target.checked)}
                className="rounded"
              />
              Выбрать все
            </label>
            <Button
              onClick={handleRerun}
              disabled={selectedIds.size === 0}
              size="sm"
              variant="outline"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Перезапустить ({selectedIds.size})
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {recipes.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">
              История пуста. Начните с поиска рецепта.
            </p>
          ) : (
            recipes.map((recipe) => (
              <RecipeHistoryItem
                key={recipe.id}
                recipe={recipe}
                isSelected={selectedIds.has(recipe.id)}
                onSelect={handleSelect}
                onView={onSelectRecipe}
                onDelete={onDeleteRecipe}
              />
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}
