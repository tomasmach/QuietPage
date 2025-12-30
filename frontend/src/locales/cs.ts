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
    signup: string;
    username: string;
    usernameOrEmail: string;
    email: string;
    password: string;
    passwordConfirm: string;
    forgotPassword: string;
    noAccount: string;
    hasAccount: string;
    createAccount: string;
    backToHome: string;
    loggingIn: string;
    signingUp: string;
    loginError: string;
    signupError: string;
  };
  landing: {
    title: string;
    tagline: string;
    getStarted: string;
    signIn: string;
    features: {
      encrypted: {
        title: string;
        description: string;
      };
      progress: {
        title: string;
        description: string;
      };
      goals: {
        title: string;
        description: string;
      };
    };
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
  dashboard: {
    greeting: {
      morning: string;
      afternoon: string;
      evening: string;
    };
    todayWords: string;
    newEntry: string;
    noEntries: string;
    recentEntries: string;
    viewAll: string;
  };
  entry: {
    titlePlaceholder: string;
    contentPlaceholder: string;
    saving: string;
    saved: string;
    delete: string;
    deleteTitle: string;
    confirmDelete: string;
    newEntry: string;
    editEntry: string;
    tags: string;
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
    signup: 'Registrovat se',
    username: 'Uživatelské jméno',
    usernameOrEmail: 'Uživatelské jméno nebo e-mail',
    email: 'E-mail',
    password: 'Heslo',
    passwordConfirm: 'Heslo znovu',
    forgotPassword: 'Zapomenuté heslo?',
    noAccount: 'Nemáš účet?',
    hasAccount: 'Máš účet?',
    createAccount: 'Vytvořit účet',
    backToHome: 'Zpět',
    loggingIn: 'Přihlašuji...',
    signingUp: 'Registruji...',
    loginError: 'Nesprávné přihlašovací údaje',
    signupError: 'Registrace se nezdařila',
  },
  landing: {
    title: 'QuietPage',
    tagline: 'Tvůj osobní prostor pro psaní a reflexi',
    getStarted: 'Začít psát',
    signIn: 'Přihlásit se',
    features: {
      encrypted: {
        title: 'Šifrované záznamy',
        description: 'Tvé myšlenky zůstanou v bezpečí',
      },
      progress: {
        title: 'Sledování pokroku',
        description: 'Motivace skrz streaky a statistiky',
      },
      goals: {
        title: 'Psací cíle',
        description: 'Denní cíle a připomínky',
      },
    },
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
  dashboard: {
    greeting: {
      morning: 'Dobré ráno',
      afternoon: 'Dobré odpoledne',
      evening: 'Dobrý večer',
    },
    todayWords: 'Slov dnes',
    newEntry: 'Nový záznam',
    noEntries: 'Zatím žádné záznamy. Začni psát!',
    recentEntries: 'Nedávné záznamy',
    viewAll: 'Zobrazit vše',
  },
  entry: {
    titlePlaceholder: 'Nadpis (volitelné)',
    contentPlaceholder: 'Začni psát...',
    saving: 'Ukládám',
    saved: 'Uloženo',
    delete: 'Smazat záznam',
    deleteTitle: 'Smazat záznam',
    confirmDelete: 'Opravdu chceš smazat tento záznam? Tuto akci nelze vrátit zpět.',
    newEntry: 'Nový záznam',
    editEntry: 'Upravit záznam',
    tags: 'Štítky',
  },
};
