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
  settings: {
    title: string;
    nav: {
      profile: string;
      goals: string;
      privacy: string;
      security: string;
      deleteAccount: string;
    };
    profile: {
      title: string;
      firstName: string;
      lastName: string;
      bio: string;
      bioHint: string;
      uploadAvatar: string;
      avatarHint: string;
      appearance: string;
      appearanceDescription: string;
      theme: string;
      themeMidnight: string;
      themePaper: string;
      language: string;
    };
    goals: {
      title: string;
      dailyWordGoal: string;
      dailyWordGoalHint: string;
      timezone: string;
      preferredWritingTime: string;
      writingTime: {
        morning: string;
        afternoon: string;
        evening: string;
      };
      reminders: string;
      enableReminders: string;
      reminderTime: string;
    };
    privacy: {
      title: string;
      notifications: string;
      emailNotifications: string;
      emailNotificationsHint: string;
      dataPrivacy: string;
      encryptionInfo: string;
      dataUsageInfo: string;
    };
    security: {
      changePassword: string;
      currentPassword: string;
      newPassword: string;
      confirmNewPassword: string;
      passwordHint: string;
      passwordsDoNotMatch: string;
      updatePassword: string;
      changeEmail: string;
      currentEmail: string;
      newEmail: string;
      passwordForEmail: string;
      passwordForEmailHint: string;
      updateEmail: string;
    };
    delete: {
      title: string;
      warning: string;
      warningItem1: string;
      warningItem2: string;
      warningItem3: string;
      password: string;
      confirmationLabel: string;
      confirmationHint: string;
      confirmationError: string;
      deleteButton: string;
    };
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
  settings: {
    title: 'Nastavení',
    nav: {
      profile: 'Profil',
      goals: 'Cíle',
      privacy: 'Soukromí',
      security: 'Zabezpečení',
      deleteAccount: 'Smazat účet',
    },
    profile: {
      title: 'Profil',
      firstName: 'Jméno',
      lastName: 'Příjmení',
      bio: 'O mně',
      bioHint: 'Krátký popis o sobě (volitelné)',
      uploadAvatar: 'Nahrát avatar',
      avatarHint: 'Max. 5 MB, formáty: JPG, PNG, GIF',
      appearance: 'Vzhled',
      appearanceDescription: 'Přizpůsobte si vzhled aplikace',
      theme: 'Motiv',
      themeMidnight: 'Midnight (tmavý)',
      themePaper: 'Paper (světlý)',
      language: 'Jazyk',
    },
    goals: {
      title: 'Psací cíle',
      dailyWordGoal: 'Denní cíl slov',
      dailyWordGoalHint: 'Doporučeno: 750 slov (asi 3 stránky)',
      timezone: 'Časová zóna',
      preferredWritingTime: 'Preferovaný čas psaní',
      writingTime: {
        morning: 'Ráno',
        afternoon: 'Odpoledne',
        evening: 'Večer',
      },
      reminders: 'Připomínky',
      enableReminders: 'Povolit denní připomínky',
      reminderTime: 'Čas připomínky',
    },
    privacy: {
      title: 'Soukromí',
      notifications: 'Oznámení',
      emailNotifications: 'E-mailová oznámení',
      emailNotificationsHint: 'Dostávat e-maily o novinkách a připomínkách',
      dataPrivacy: 'Ochrana dat',
      encryptionInfo: 'Všechny tvé záznamy jsou šifrovány pomocí AES-256 šifrování.',
      dataUsageInfo: 'Tvá data nikdy nesdílíme s třetími stranami.',
    },
    security: {
      changePassword: 'Změnit heslo',
      currentPassword: 'Současné heslo',
      newPassword: 'Nové heslo',
      confirmNewPassword: 'Potvrdit nové heslo',
      passwordHint: 'Minimálně 8 znaků',
      passwordsDoNotMatch: 'Hesla se neshodují',
      updatePassword: 'Aktualizovat heslo',
      changeEmail: 'Změnit e-mail',
      currentEmail: 'Současný e-mail',
      newEmail: 'Nový e-mail',
      passwordForEmail: 'Heslo pro potvrzení',
      passwordForEmailHint: 'Pro změnu e-mailu zadej své heslo',
      updateEmail: 'Aktualizovat e-mail',
    },
    delete: {
      title: 'Smazat účet',
      warning: 'Tato akce je nevratná!',
      warningItem1: 'Všechny tvé záznamy budou trvale smazány',
      warningItem2: 'Tvůj profil a nastavení budou odstraněny',
      warningItem3: 'Tuto akci nelze vrátit zpět',
      password: 'Heslo',
      confirmationLabel: 'Potvrzení',
      confirmationHint: 'Pro potvrzení napiš "{word}"',
      confirmationError: 'Napiš "{word}" pro potvrzení',
      deleteButton: 'Trvale smazat účet',
    },
  },
};
