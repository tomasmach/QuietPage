export const cs = {
  nav: {
    write: 'Psát',
    stats: 'Statistiky',
    archive: 'Archiv',
    settings: 'Nastavení',
  },
  meta: {
    version: 'Verze 0.9.1 Beta',
    wordsToday: 'Slov dnes',
    progress: 'Progress',
    goalMet: 'Cíl splněn',
    currentStreak: 'Aktuální Streak',
    moodCheck: 'Nálada',
    recentDays: 'Poslední Dny',
    wordsSuffix: 'slov',
  },
  auth: {
    login: 'Přihlásit se',
    logout: 'Odhlásit se',
    register: 'Registrace',
    username: 'Uživatelské jméno',
    email: 'E-mail',
    password: 'Heslo',
    passwordConfirm: 'Heslo znovu',
  },
  themes: {
    paper: 'Paper (Světlý)',
    midnight: 'Midnight (Tmavý)',
  },
  common: {
    save: 'Uložit',
    cancel: 'Zrušit',
    delete: 'Smazat',
    loading: 'Načítání...',
  },
} as const;

export type Translations = typeof cs;
