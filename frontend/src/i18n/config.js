/**
 * i18n Configuration for Africa Business Bridge
 * 
 * Supports multiple languages: Italian, English, Swahili, Amharic
 */

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Import translation files
import itTranslations from './locales/it/translation.json';
import enTranslations from './locales/en/translation.json';
import swTranslations from './locales/sw/translation.json';
import amTranslations from './locales/am/translation.json';

const resources = {
  it: { translation: itTranslations },
  en: { translation: enTranslations },
  sw: { translation: swTranslations },
  am: { translation: amTranslations },
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    defaultNS: 'translation',
    interpolation: {
      escapeValue: false, // React already escapes values
    },
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
    },
  });

export default i18n;

