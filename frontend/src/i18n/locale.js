export function resolveUiLocale(language = 'en') {
  return language === 'ne' ? 'ne-NP' : 'en-US';
}

export function resolveDocumentLanguage(language = 'en') {
  return language === 'ne' ? 'ne' : 'en';
}
