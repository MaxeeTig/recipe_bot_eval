import React from 'react';
import { Search } from 'lucide-react';
import { Input } from './ui/input';
import { Button } from './ui/button';

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  onSearch: () => void;
  isLoading?: boolean;
}

export function SearchBar({ value, onChange, onSearch, isLoading = false }: SearchBarProps) {
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !isLoading) {
      onSearch();
    }
  };

  return (
    <div className="flex gap-3">
      <div className="flex-1 relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
        <Input
          type="text"
          placeholder="Например: паста карбонара"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyPress={handleKeyPress}
          className="pl-10"
          disabled={isLoading}
        />
      </div>
      <Button onClick={onSearch} disabled={isLoading || !value.trim()}>
        {isLoading ? 'Поиск...' : 'Найти рецепт'}
      </Button>
    </div>
  );
}
