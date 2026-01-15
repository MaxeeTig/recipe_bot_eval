import React, { useState } from 'react';
import { SearchBar } from './SearchBar';
import { RecipeHistory } from './RecipeHistory';
import { RecipeEntry } from '../types/recipe';
import { toast } from 'sonner';

interface HomePageProps {
  recipes: RecipeEntry[];
  onSearch: (query: string) => void;
  onSelectRecipe: (id: string) => void;
  onRerunRecipes: (ids: string[]) => void;
  onDeleteRecipe: (id: string) => void;
  isLoading: boolean;
}

export function HomePage({ recipes, onSearch, onSelectRecipe, onRerunRecipes, onDeleteRecipe, isLoading }: HomePageProps) {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = () => {
    if (searchQuery.trim()) {
      onSearch(searchQuery.trim());
      toast.success('Поиск запущен', {
        description: `Ищем рецепт: ${searchQuery}`
      });
    }
  };

  const handleRerun = (ids: string[]) => {
    onRerunRecipes(ids);
    toast.info('Перезапуск обработки', {
      description: `Выбрано рецептов: ${ids.length}`
    });
  };

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h1>Поиск рецептов</h1>
        <p className="text-muted-foreground">
          Введите название блюда или ингредиенты для поиска через Tavily
        </p>
      </div>

      <SearchBar
        value={searchQuery}
        onChange={setSearchQuery}
        onSearch={handleSearch}
        isLoading={isLoading}
      />

      <RecipeHistory
        recipes={recipes}
        onSelectRecipe={onSelectRecipe}
        onRerunRecipes={handleRerun}
        onDeleteRecipe={onDeleteRecipe}
      />
    </div>
  );
}
