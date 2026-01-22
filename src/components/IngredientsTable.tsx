import React from 'react';
import { Ingredient } from '../types/recipe';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from './ui/table';

interface IngredientsTableProps {
  ingredients: Ingredient[];
  onChange: (index: number, field: keyof Ingredient, value: any) => void;
}

export function IngredientsTable({ ingredients, onChange }: IngredientsTableProps) {
  return (
    <div className="border rounded-md">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Ингредиент</TableHead>
            <TableHead>Кол-во (LLM)</TableHead>
            <TableHead>Ед.изм (LLM)</TableHead>
            <TableHead>Оригинал</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {ingredients.map((ingredient, index) => (
            <TableRow key={index}>
              <TableCell>
                <input
                  type="text"
                  value={ingredient.name}
                  onChange={(e) => onChange(index, 'name', e.target.value)}
                  className="w-full bg-transparent border-none outline-none"
                />
              </TableCell>
              <TableCell>
                <input
                  type="text"
                  value={ingredient.amountLLM}
                  onChange={(e) => onChange(index, 'amountLLM', e.target.value)}
                  className="w-full bg-transparent border-none outline-none"
                />
              </TableCell>
              <TableCell>
                <input
                  type="text"
                  value={ingredient.unitLLM}
                  onChange={(e) => onChange(index, 'unitLLM', e.target.value)}
                  className="w-full bg-transparent border-none outline-none"
                />
              </TableCell>
              <TableCell className="text-muted-foreground">
                {ingredient.original}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
