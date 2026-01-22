import type { Settings } from '../types/recipe';
import { defaultSettings } from './mockData';
import { logger } from './logger';

const STORAGE_KEYS = {
  SETTINGS: 'recipe-bot-settings',
} as const;

/**
 * Loads settings from localStorage, falling back to default settings if unavailable.
 * Handles errors gracefully (localStorage disabled, invalid JSON, etc.)
 */
export function loadSettings(): Settings {
  try {
    if (typeof window === 'undefined' || !window.localStorage) {
      logger.warn('localStorage not available, using default settings');
      return defaultSettings;
    }

    const stored = window.localStorage.getItem(STORAGE_KEYS.SETTINGS);
    if (!stored) {
      logger.debug('No settings found in localStorage, using defaults');
      return defaultSettings;
    }

    const parsed = JSON.parse(stored) as Partial<Settings>;
    
    // Validate that parsed data has the expected structure
    // Merge with defaults to ensure all required fields are present
    const settings: Settings = {
      provider: parsed.provider ?? defaultSettings.provider,
      modelParsing: parsed.modelParsing ?? defaultSettings.modelParsing,
      modelAnalysis: parsed.modelAnalysis ?? defaultSettings.modelAnalysis,
    };

    logger.debug('Settings loaded from localStorage', settings);
    return settings;
  } catch (error) {
    const err = error instanceof Error ? error : new Error(String(error));
    logger.error('Failed to load settings from localStorage', { error: err.message }, err);
    return defaultSettings;
  }
}

/**
 * Saves settings to localStorage.
 * Handles errors gracefully (localStorage disabled, quota exceeded, etc.)
 */
export function saveSettings(settings: Settings): void {
  try {
    if (typeof window === 'undefined' || !window.localStorage) {
      logger.warn('localStorage not available, settings not saved');
      return;
    }

    window.localStorage.setItem(STORAGE_KEYS.SETTINGS, JSON.stringify(settings));
    logger.debug('Settings saved to localStorage', settings);
  } catch (error) {
    const err = error instanceof Error ? error : new Error(String(error));
    // Check if it's a quota exceeded error
    if (err.name === 'QuotaExceededError' || err.message.includes('quota')) {
      logger.warn('localStorage quota exceeded, settings not saved');
    } else {
      logger.error('Failed to save settings to localStorage', { error: err.message }, err);
    }
  }
}
