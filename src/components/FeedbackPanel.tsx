import React from 'react';
import { Star } from 'lucide-react';
import { RecipeFeedback } from '../types/recipe';
import { Slider } from './ui/slider';
import { Textarea } from './ui/textarea';
import { Checkbox } from './ui/checkbox';
import { Label } from './ui/label';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';

interface FeedbackPanelProps {
  feedback: RecipeFeedback;
  onChange: (feedback: RecipeFeedback) => void;
  onSave: () => void;
  onSaveWithEdits: () => void;
}

export function FeedbackPanel({ feedback, onChange, onSave, onSaveWithEdits }: FeedbackPanelProps) {
  const renderStars = (value: number) => {
    return (
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`w-5 h-5 ${
              star <= value ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'
            }`}
          />
        ))}
      </div>
    );
  };

  const sliderConfig = [
    { key: 'ingredientAccuracy' as const, label: 'Точность ингредиентов' },
    { key: 'dataCompleteness' as const, label: 'Полнота данных' },
    { key: 'originalMatch' as const, label: 'Соответствие оригиналу' },
    { key: 'overallQuality' as const, label: 'Общее качество' }
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Оценка качества</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {sliderConfig.map(({ key, label }) => (
          <div key={key} className="space-y-2">
            <div className="flex items-center justify-between">
              <Label>{label}</Label>
              <div className="flex items-center gap-2">
                {renderStars(feedback[key])}
                <span className="text-sm text-muted-foreground w-8 text-right">
                  {feedback[key]}
                </span>
              </div>
            </div>
            <Slider
              value={[feedback[key]]}
              onValueChange={([value]) => onChange({ ...feedback, [key]: value })}
              min={1}
              max={5}
              step={1}
              className="w-full"
            />
          </div>
        ))}

        <div className="space-y-2">
          <Label>Комментарии / замечания</Label>
          <Textarea
            value={feedback.comments}
            onChange={(e) => onChange({ ...feedback, comments: e.target.value })}
            placeholder="Опишите замечания или предложения..."
            rows={4}
          />
        </div>

        <div className="flex items-center gap-2">
          <Checkbox
            id="production-ready"
            checked={feedback.readyForProduction}
            onCheckedChange={(checked) =>
              onChange({ ...feedback, readyForProduction: checked as boolean })
            }
          />
          <Label htmlFor="production-ready" className="cursor-pointer">
            Рецепт пригоден для продакшена
          </Label>
        </div>

        <div className="flex gap-2 pt-4">
          <Button onClick={onSave} className="flex-1 bg-green-600 hover:bg-green-700">
            Сохранить оценку
          </Button>
          <Button onClick={onSaveWithEdits} variant="outline" className="flex-1">
            Исправить и сохранить
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
