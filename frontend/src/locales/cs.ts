export interface Translations {
  nav: {
    dashboard: string;
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
    morningMind: string;
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
    hero: {
      headline: string;
      subheadline: string;
    };
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
      privacy: {
        title: string;
        description: string;
      };
      moodTracking: {
        title: string;
        description: string;
      };
      streaks: {
        title: string;
        description: string;
      };
      insights: {
        title: string;
        description: string;
      };
    };
    finalCta: {
      headline: string;
      subtext: string;
    };
    trust: {
      encrypted: string;
      private: string;
    };
  };
  themes: {
    paper: string;
    midnight: string;
  };
  theme: {
    light: string;
    dark: string;
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
    longestStreak: string;
    totalEntries: string;
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
    loadError: string;
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
  onboarding: {
    progress: string;
    skip: string;
    continue: string;
    back: string;
    finish: string;
    finishing: string;
    step1: {
      title: string;
      description: string;
      theme: string;
      language: string;
    };
    step2: {
      title: string;
      description: string;
      dailyGoal: string;
      customGoalPlaceholder: string;
      writingTime: string;
    };
  };
  toast: {
    close: string;
    saveSuccess: string;
    saveError: string;
    networkError: string;
    unknownError: string;
    loginError: string;
    loginSuccess: string;
    logoutSuccess: string;
    registerError: string;
    accountDeactivated: string;
    profileUpdated: string;
    avatarUploaded: string;
    avatarRemoved: string;
    passwordChanged: string;
    emailChanged: string;
    goalsUpdated: string;
    privacyUpdated: string;
    emailVerificationSent: string;
    entrySaved: string;
    entryDeleted: string;
    accountDeleted: string;
  };
  statistics: {
    title: string;
    writingPatterns: string;
    viewModes: {
      milestones: string;
      patterns: string;
    };
    consistencyRate: {
      title: string;
      description: string;
      percentage: string;
    };
    frequencyHeatmap: {
      title: string;
      noWriting: string;
      words: string;
      less: string;
      more: string;
    };
    timeOfDayChart: {
      title: string;
      notEnoughData: string;
      morning: string;
      afternoon: string;
      evening: string;
      night: string;
      morningDesc: string;
      afternoonDesc: string;
      eveningDesc: string;
      nightDesc: string;
      entries: string;
    };
    dayOfWeekChart: {
      title: string;
      notEnoughData: string;
      yAxisLabel: string;
      mostProductive: string;
      mostProductiveDay: string;
      daySingular: string;
      daysPlural: string;
      monday: string;
      mondayAbbr: string;
      tuesday: string;
      tuesdayAbbr: string;
      wednesday: string;
      wednesdayAbbr: string;
      thursday: string;
      thursdayAbbr: string;
      friday: string;
      fridayAbbr: string;
      saturday: string;
      saturdayAbbr: string;
      sunday: string;
      sundayAbbr: string;
    };
    streakHistory: {
      title: string;
      noData: string;
      longest: string;
      current: string;
      daySingular: string;
      daysPlural: string;
      encouragement: string;
      newRecord: string;
      matchingRecord: string;
    };
    summaryCards: {
      avgMood: string;
      totalWords: string;
      avgPerDay: string;
      goalRate: string;
      ratedEntries: string;
      entries: string;
      words: string;
      daysMetGoal: string;
    };
    moodTimeline: {
      title: string;
      notEnoughData: string;
    };
    wordCountTimeline: {
      title: string;
      noData: string;
      wordsLabel: string;
    };
    error: {
      unableToLoad: string;
      retry: string;
    };
    timeRange: {
      last7Days: string;
      last30Days: string;
      last90Days: string;
      lastYear: string;
      allTime: string;
    };
    tagAnalytics: {
      title: string;
      entries: string;
      avgWords: string;
      avgMood: string;
      noTags: string;
    };
    moodDistribution: {
      title: string;
      rating: string;
      entries: string;
      noData: string;
    };
    moodTrend: {
      improving: string;
      declining: string;
      stable: string;
    };
    bestDay: {
      title: string;
      words: string;
      entries: string;
      noData: string;
    };
    milestones: {
      title: string;
      entries: string;
      words: string;
      streaks: string;
      achieved: string;
      noData: string;
    };
    goalStreak: {
      title: string;
      current: string;
      longest: string;
      days: string;
      perDay: string;
      active: string;
      inactive: string;
    };
    records: {
      title: string;
      longestEntry: string;
      mostProductiveDay: string;
      longestStreak: string;
      longestGoalStreak: string;
      words: string;
      days: string;
      entries: string;
      noRecords: string;
    };
  };
}

export const cs: Translations = {
  nav: {
    dashboard: 'Dashboard',
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
    morningMind: 'Ranní Mysl',
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
    hero: {
      headline: 'Tvůj soukromý prostor pro mindful psaní',
      subheadline: 'Vyjadřuj se svobodně, sleduj své emocionální zdraví a buduj trvalé návyky psaní',
    },
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
      privacy: {
        title: 'Tvůj Soukromý Prostor',
        description: 'Tvé myšlenky jsou šifrované a zůstávají zcela soukromé. Přístup k nim máš jen ty.',
      },
      moodTracking: {
        title: 'Sleduj Svou Emocionální Cestu',
        description: 'Zaznamenej si každý den, jak se cítíš. Vizualizuj své emocionální vzory a objevuj, co ovlivňuje tvou pohodu.',
      },
      streaks: {
        title: 'Buduj Trvalé Návyky',
        description: 'Zůstaň motivovaný díky sledování streaks a denních cílů. Oslavuj svou konzistenci.',
      },
      insights: {
        title: 'Porozuměj Svým Vzorům',
        description: 'Krásné grafy ukazují tvé psací trendy, počty slov a nálady.',
      },
    },
    finalCta: {
      headline: 'Začni Svou Cestu Mindful Psaní',
      subtext: 'Zdarma na začátek, tvé soukromí garantováno',
    },
    trust: {
      encrypted: 'Šifrováno',
      private: '100% Soukromé',
    },
  },
  themes: {
    paper: 'Paper (Světlý)',
    midnight: 'Midnight (Tmavý)',
  },
  theme: {
    light: 'Světlý režim',
    dark: 'Tmavý režim',
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
    longestStreak: 'Nejdelší',
    totalEntries: 'Celkem záznamů',
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
    loadError: 'Chyba při načítání záznamu. Zkuste obnovit stránku.',
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
  onboarding: {
    progress: 'Krok {current} z {total}',
    skip: 'Přeskočit',
    continue: 'Pokračovat',
    back: 'Zpět',
    finish: 'Dokončit',
    finishing: 'Dokončuji...',
    step1: {
      title: 'Personalizace',
      description: 'Přizpůsob si QuietPage podle svých preferencí',
      theme: 'Motiv',
      language: 'Jazyk',
    },
    step2: {
      title: 'Psací cíle',
      description: 'Nastav si denní cíl a preferovaný čas psaní',
      dailyGoal: 'Denní cíl slov',
      customGoalPlaceholder: 'Vlastní hodnota',
      writingTime: 'Preferovaný čas psaní',
    },
  },
  toast: {
    close: 'Zavřít',
    // Obecné
    saveSuccess: 'Změny byly uloženy',
    saveError: 'Nepodařilo se uložit změny',
    networkError: 'Chyba připojení. Zkuste to znovu.',
    unknownError: 'Nastala neočekávaná chyba',
    // Auth
    loginError: 'Neplatné přihlašovací údaje',
    loginSuccess: 'Přihlášení úspěšné',
    logoutSuccess: 'Odhlášení úspěšné',
    registerError: 'Registrace se nezdařila',
    accountDeactivated: 'Tento účet byl deaktivován',
    // Profil
    profileUpdated: 'Profil byl aktualizován',
    avatarUploaded: 'Avatar byl nahrán',
    avatarRemoved: 'Avatar byl odstraněn',
    // Heslo a email
    passwordChanged: 'Heslo bylo změněno',
    emailChanged: 'Email byl změněn',
    // Cíle
    goalsUpdated: 'Cíle byly aktualizovány',
    // Soukromí
    privacyUpdated: 'Nastavení soukromí bylo aktualizováno',
    emailVerificationSent: 'Ověřovací e-mail byl odeslán na vaši novou e-mailovou adresu',
    // Záznamy
    entrySaved: 'Záznam byl uložen',
    entryDeleted: 'Záznam byl smazán',
    // Účet
    accountDeleted: 'Účet byl smazán',
  },
  statistics: {
    title: 'STATISTIKY',
    writingPatterns: 'PSACÍ VZORY',
    viewModes: {
      milestones: 'Milníky a rekordy',
      patterns: 'Psací vzory',
    },
    consistencyRate: {
      title: 'KONZISTENCE PSANÍ',
      description: 'Procento dní, kdy jsi psal(a) ze sledovaného období',
      percentage: '{rate}% konzistence',
    },
    frequencyHeatmap: {
      title: 'ČETNOST PSANÍ (90 DNÍ)',
      noWriting: 'Žádné psaní',
      words: 'slov',
      less: 'MÉNĚ',
      more: 'VÍCE',
    },
    timeOfDayChart: {
      title: 'DENNÍ DOBA PSANÍ',
      notEnoughData: 'Nedostatek dat',
      morning: 'Ráno',
      afternoon: 'Odpoledne',
      evening: 'Večer',
      night: 'Noc',
      morningDesc: 'Ráno: 5:00 – 11:59',
      afternoonDesc: 'Odpoledne: 12:00 – 17:59',
      eveningDesc: 'Večer: 18:00 – 23:59',
      nightDesc: 'Noc: 0:00 – 4:59',
      entries: 'záznamů',
    },
    dayOfWeekChart: {
      title: 'AKTIVITA V TÝDNU',
      notEnoughData: 'Nedostatek dat',
      yAxisLabel: 'Počet dní',
      mostProductive: 'Nejproduktivnější',
      mostProductiveDay: 'Nejproduktivnější den',
      daySingular: 'den',
      daysPlural: 'dní',
      monday: 'Pondělí',
      mondayAbbr: 'Po',
      tuesday: 'Úterý',
      tuesdayAbbr: 'Út',
      wednesday: 'Středa',
      wednesdayAbbr: 'St',
      thursday: 'Čtvrtek',
      thursdayAbbr: 'Čt',
      friday: 'Pátek',
      fridayAbbr: 'Pá',
      saturday: 'Sobota',
      saturdayAbbr: 'So',
      sunday: 'Neděle',
      sundayAbbr: 'Ne',
    },
    streakHistory: {
      title: 'HISTORIE STREAKU',
      noData: 'Zatím žádná data o streaku',
      longest: 'Nejdelší',
      current: 'Aktuální',
      daySingular: 'den',
      daysPlural: 'dní',
      encouragement: 'Tvůj nejdelší streak byl {days} dní – můžeš ho překonat!',
      newRecord: 'Gratulujeme! Tvůj aktuální streak ({days} dní) je nový rekord!',
      matchingRecord: 'Skvělé! Vyrovnal jsi svůj rekord {days} dní!',
    },
    summaryCards: {
      avgMood: 'PRŮMĚRNÁ NÁLADA',
      totalWords: 'CELKEM SLOV',
      avgPerDay: 'PRŮMĚR ZA DEN',
      goalRate: 'ÚSPĚŠNOST CÍLE',
      ratedEntries: 'hodnocených záznamů',
      entries: 'záznamů',
      words: 'slov',
      daysMetGoal: 'dní splněn cíl',
    },
    moodTimeline: {
      title: 'VÝVOJ NÁLADY',
      notEnoughData: 'NEDOSTATEK DAT PRO ZOBRAZENÍ TRENDŮ NÁLADY',
    },
    wordCountTimeline: {
      title: 'VÝVOJ POČTU SLOV',
      noData: 'ŽÁDNÁ DATA O PSANÍ',
      wordsLabel: 'Slov',
    },
    error: {
      unableToLoad: 'NELZE NAČÍST STATISTIKY',
      retry: 'ZKUSIT ZNOVU',
    },
    timeRange: {
      last7Days: 'POSLEDNÍCH 7 DNÍ',
      last30Days: 'POSLEDNÍCH 30 DNÍ',
      last90Days: 'POSLEDNÍCH 90 DNÍ',
      lastYear: 'POSLEDNÍ ROK',
      allTime: 'CELÉ OBDOBÍ',
    },
    tagAnalytics: {
      title: 'ANALÝZA ŠTÍTKŮ',
      entries: 'zápisů',
      avgWords: 'prům. slov',
      avgMood: 'prům. nálada',
      noTags: 'Zatím žádné štítky',
    },
    moodDistribution: {
      title: 'ROZLOŽENÍ NÁLAD',
      rating: 'Hodnocení',
      entries: 'zápisů',
      noData: 'Zatím žádná data o náladě',
    },
    moodTrend: {
      improving: 'Zlepšuje se',
      declining: 'Zhoršuje se',
      stable: 'Stabilní',
    },
    bestDay: {
      title: 'NEJLEPŠÍ DEN PSANÍ',
      words: 'slov',
      entries: 'zápisů',
      noData: 'Piš dál a vytvoř si rekord!',
    },
    milestones: {
      title: 'MILNÍKY',
      entries: 'Zápisů',
      words: 'Slov',
      streaks: 'Dní v sérii',
      achieved: 'Dosaženo!',
      noData: 'Zatím žádné milníky',
    },
    goalStreak: {
      title: 'SÉRIE 750 SLOV',
      current: 'Aktuální',
      longest: 'Nejdelší',
      days: 'dní',
      perDay: 'slov/den cíl',
      active: 'Jsi v plamenech!',
      inactive: 'Začni novou sérii dnes!',
    },
    records: {
      title: 'OSOBNÍ REKORDY',
      longestEntry: 'Nejdelší zápis',
      mostProductiveDay: 'Nejproduktivnější den',
      longestStreak: 'Nejdelší série',
      longestGoalStreak: 'Nejdelší série 750',
      words: 'slov',
      days: 'dní',
      entries: 'zápisů',
      noRecords: 'Začni psát a vytvoř si rekordy!',
    },
  },
};
