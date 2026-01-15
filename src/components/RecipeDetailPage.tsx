import React, { useState } from 'react';
import { ArrowLeft } from 'lucide-react';
import { RecipeEntry, RecipeData, RecipeFeedback } from '../types/recipe';
import { OriginalRecipeView } from './OriginalRecipeView';
import { StructuredRecipeView } from './StructuredRecipeView';
import { FeedbackPanel } from './FeedbackPanel';
import { Button } from './ui/button';
import { toast } from 'sonner';

interface RecipeDetailPageProps {
  recipe: RecipeEntry;
  onBack: () => void;
  onSaveFeedback: (recipeId: string, feedback: RecipeFeedback, recipeData: RecipeData) => void;
}

export function RecipeDetailPage({ recipe, onBack, onSaveFeedback }: RecipeDetailPageProps) {
  const [recipeData, setRecipeData] = useState<RecipeData>(
    recipe.recipeData || {} as RecipeData
  );
  const [feedback, setFeedback] = useState<RecipeFeedback>(
    recipe.feedback || {
      ingredientAccuracy: 3,
      dataCompleteness: 3,
      originalMatch: 3,
      overallQuality: 3,
      comments: '',
      readyForProduction: false
    }
  );

  if (!recipe.source || !recipe.recipeData) {
    return (
      <div className="space-y-4">
        <Button onClick={onBack} variant="ghost" size="sm">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Назад
        </Button>
        <div className="text-center py-12">
          <p className="text-muted-foreground">Данные рецепта не найдены</p>
        </div>
      </div>
    );
  }

  const handleSave = () => {
    onSaveFeedback(recipe.id, feedback, recipeData);
    toast.success('Оценка сохранена', {
      description: 'Ваша обратная связь успешно записана'
    });
  };

  const handleSaveWithEdits = () => {
    onSaveFeedback(recipe.id, feedback, recipeData);
    toast.success('Изменения сохранены', {
      description: 'Исправленные данные отправлены в систему'
    });
  };

  return (
    <div className="space-y-4">
      <Button onClick={onBack} variant="ghost" size="sm">
        <ArrowLeft className="w-4 h-4 mr-2" />
        Назад к списку
      </Button>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column - Original */}
        <div className="space-y-6">
          <OriginalRecipeView
            source={recipe.source}
            metadata={{
              date: recipe.recipeData.searchDate,
              model: recipe.recipeData.modelUsed,
              promptVersion: recipe.recipeData.promptVersion
            }}
          />
        </div>

        {/* Right Column - Structured + Feedback */}
        <div className="space-y-6">
          <StructuredRecipeView recipeData={recipeData} onChange={setRecipeData} />
          <FeedbackPanel
            feedback={feedback}
            onChange={setFeedback}
            onSave={handleSave}
            onSaveWithEdits={handleSaveWithEdits}
          />
        </div>
      </div>
    </div>
  );
}
