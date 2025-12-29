export interface Translations {
  nav: {
    write: string;
    stats: string;
    archive: string;
    settings: string;
  };
  meta: {
    version: string;
    wordsToday: string;
    progress: string;
    goalMet: string;
    currentStreak: string;
    moodCheck: string;
    recentDays: string;
    wordsSuffix: string;
  };
  auth: {
    login: string;
    logout: string;
    register: string;
    username: string;
    email: string;
    password: string;
    passwordConfirm: string;
  };
  themes: {
    paper: string;
    midnight: string;
  };
  common: {
    save: string;
    cancel: string;
    delete: string;
    loading: string;
  };
}

export const cs: Translations = {
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
};
