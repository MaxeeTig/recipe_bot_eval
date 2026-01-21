import React from 'react';
import type { Settings } from '../types/recipe';
import { Input } from './ui/input';
import { Label } from './ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { PROVIDERS } from '../lib/mockData';

interface SettingsPanelProps {
  settings: Settings;
  onChange: (settings: Settings) => void;
}

export function SettingsPanel({ settings, onChange }: SettingsPanelProps) {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Провайдер LLM</CardTitle>
          <CardDescription>
            Выберите провайдера для парсинга и анализа рецептов
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Select
            value={settings.provider}
            onValueChange={(value) => onChange({ ...settings, provider: value })}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {PROVIDERS.map((p) => (
                <SelectItem key={p} value={p}>
                  {p}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Модель для парсинга</CardTitle>
          <CardDescription>
            Модель для извлечения структуры из рецепта. Пусто — дефолт бэкенда.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Input
            value={settings.modelParsing}
            onChange={(e) => onChange({ ...settings, modelParsing: e.target.value })}
            placeholder="Например: gpt-4o-mini или оставьте пустым"
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Модель для анализа ошибок</CardTitle>
          <CardDescription>
            Модель для анализа неудачного парсинга. Пусто — дефолт бэкенда.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Input
            value={settings.modelAnalysis}
            onChange={(e) => onChange({ ...settings, modelAnalysis: e.target.value })}
            placeholder="Например: gpt-4o или оставьте пустым"
          />
        </CardContent>
      </Card>

      <div className="bg-muted/50 border rounded-lg p-4">
        <p className="text-sm text-muted-foreground">
          Изменения применяются к новым операциям (поиск, парсинг, анализ). API‑ключи задаются в .env на бэкенде.
        </p>
      </div>
    </div>
  );
}
