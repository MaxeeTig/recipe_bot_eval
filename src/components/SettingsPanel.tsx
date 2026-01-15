import React, { useState } from 'react';
import { Eye, EyeOff, RotateCcw } from 'lucide-react';
import { Settings as SettingsType } from '../types/recipe';
import { defaultSettings } from '../lib/mockData';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Slider } from './ui/slider';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Separator } from './ui/separator';
import { toast } from 'sonner';

interface SettingsPanelProps {
  settings: SettingsType;
  onChange: (settings: SettingsType) => void;
}

export function SettingsPanel({ settings, onChange }: SettingsPanelProps) {
  const [showTavilyKey, setShowTavilyKey] = useState(false);
  const [showOpenAIKey, setShowOpenAIKey] = useState(false);

  const handleResetPrompt = () => {
    onChange({ ...settings, systemPrompt: defaultSettings.systemPrompt });
    toast.info('Промпт сброшен', {
      description: 'Восстановлен шаблон по умолчанию'
    });
  };

  const models = [
    'gpt-4o-mini',
    'gpt-4o',
    'gpt-4-turbo',
    'claude-3-haiku',
    'claude-3-sonnet',
    'claude-3-opus'
  ];

  return (
    <div className="space-y-6">
      {/* API Keys */}
      <Card>
        <CardHeader>
          <CardTitle>API-ключи</CardTitle>
          <CardDescription>
            Введите свои ключи для доступа к внешним сервисам
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="tavily-key">Tavily API Key</Label>
            <div className="relative">
              <Input
                id="tavily-key"
                type={showTavilyKey ? 'text' : 'password'}
                value={settings.tavilyApiKey}
                onChange={(e) => onChange({ ...settings, tavilyApiKey: e.target.value })}
                className="pr-10"
              />
              <button
                type="button"
                onClick={() => setShowTavilyKey(!showTavilyKey)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                {showTavilyKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="openai-key">OpenAI API Key</Label>
            <div className="relative">
              <Input
                id="openai-key"
                type={showOpenAIKey ? 'text' : 'password'}
                value={settings.openaiApiKey}
                onChange={(e) => onChange({ ...settings, openaiApiKey: e.target.value })}
                className="pr-10"
              />
              <button
                type="button"
                onClick={() => setShowOpenAIKey(!showOpenAIKey)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                {showOpenAIKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Model Selection */}
      <Card>
        <CardHeader>
          <CardTitle>Модель LLM</CardTitle>
          <CardDescription>
            Выберите модель для обработки рецептов
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Select
            value={settings.selectedModel}
            onValueChange={(value) => onChange({ ...settings, selectedModel: value })}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {models.map((model) => (
                <SelectItem key={model} value={model}>
                  {model}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      {/* System Prompt */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Системный промпт</CardTitle>
              <CardDescription>
                Инструкции для модели по извлечению данных из рецептов
              </CardDescription>
            </div>
            <Button onClick={handleResetPrompt} variant="outline" size="sm">
              <RotateCcw className="w-4 h-4 mr-2" />
              Сбросить
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <Textarea
            value={settings.systemPrompt}
            onChange={(e) => onChange({ ...settings, systemPrompt: e.target.value })}
            rows={12}
            className="font-mono text-sm"
          />
        </CardContent>
      </Card>

      {/* Generation Parameters */}
      <Card>
        <CardHeader>
          <CardTitle>Параметры генерации</CardTitle>
          <CardDescription>
            Настройки, влияющие на поведение модели
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label>Temperature</Label>
              <span className="text-sm text-muted-foreground">
                {settings.temperature.toFixed(1)}
              </span>
            </div>
            <Slider
              value={[settings.temperature]}
              onValueChange={([value]) => onChange({ ...settings, temperature: value })}
              min={0}
              max={1}
              step={0.1}
            />
            <p className="text-xs text-muted-foreground">
              Более низкие значения = более предсказуемый результат
            </p>
          </div>

          <Separator />

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label>Max Tokens</Label>
              <span className="text-sm text-muted-foreground">
                {settings.maxTokens}
              </span>
            </div>
            <Slider
              value={[settings.maxTokens]}
              onValueChange={([value]) => onChange({ ...settings, maxTokens: value })}
              min={500}
              max={4000}
              step={100}
            />
          </div>
        </CardContent>
      </Card>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-sm text-yellow-800">
          ⚠️ <strong>Внимание:</strong> Все изменения в настройках применяются только к новым запросам.
          Существующие рецепты остаются без изменений.
        </p>
      </div>
    </div>
  );
}
