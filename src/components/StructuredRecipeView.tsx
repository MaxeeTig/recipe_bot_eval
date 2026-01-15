import React, { useState } from 'react';
import { RecipeData, RecipeFeedback } from '../types/recipe';
import { IngredientsTable } from './IngredientsTable';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { ScrollArea } from './ui/scroll-area';

interface StructuredRecipeViewProps {
  recipeData: RecipeData;
  onChange: (data: RecipeData) => void;
}

export function StructuredRecipeView({ recipeData, onChange }: StructuredRecipeViewProps) {
  const handleIngredientChange = (index: number, field: any, value: any) => {
    const newIngredients = [...recipeData.ingredients];
    newIngredients[index] = { ...newIngredients[index], [field]: value };
    onChange({ ...recipeData, ingredients: newIngredients });
  };

  const handleStepChange = (index: number, value: string) => {
    const newSteps = [...recipeData.steps];
    newSteps[index] = value;
    onChange({ ...recipeData, steps: newSteps });
  };

  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Обработано ИИ</CardTitle>
          <Badge variant="secondary">v{recipeData.promptVersion}</Badge>
        </div>
      </CardHeader>
      <CardContent className="flex-1 overflow-auto">
        <ScrollArea className="h-full pr-4">
          <div className="space-y-6">
            {/* Basic Info */}
            <div className="space-y-4">
              <div>
                <Label>Название блюда</Label>
                <Input
                  value={recipeData.dishName}
                  onChange={(e) => onChange({ ...recipeData, dishName: e.target.value })}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Время готовки (минут)</Label>
                  <Input
                    type="number"
                    value={recipeData.cookingTime}
                    onChange={(e) =>
                      onChange({ ...recipeData, cookingTime: parseInt(e.target.value) || 0 })
                    }
                  />
                </div>
                <div>
                  <Label>Количество порций</Label>
                  <Input
                    type="number"
                    value={recipeData.servings}
                    onChange={(e) =>
                      onChange({ ...recipeData, servings: parseInt(e.target.value) || 0 })
                    }
                  />
                </div>
              </div>
            </div>

            {/* Ingredients Table */}
            <div className="space-y-2">
              <Label>Список ингредиентов</Label>
              <IngredientsTable
                ingredients={recipeData.ingredients}
                onChange={handleIngredientChange}
              />
            </div>

            {/* Steps */}
            <div className="space-y-2">
              <Label>Пошаговая инструкция</Label>
              <div className="space-y-2">
                {recipeData.steps.map((step, index) => (
                  <div key={index} className="flex gap-2">
                    <span className="text-muted-foreground shrink-0 w-6">{index + 1}.</span>
                    <textarea
                      value={step}
                      onChange={(e) => handleStepChange(index, e.target.value)}
                      className="flex-1 min-h-[60px] p-2 border rounded-md resize-y"
                    />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
