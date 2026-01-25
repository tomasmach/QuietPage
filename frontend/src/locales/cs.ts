export interface Translations {
  nav: {
    dashboard: string;
    write: string;
    stats: string;
    archive: string;
    settings: string;
  };
  archive: {
    totalEntries: string;
    errorLoading: string;
    page: string;
    previous: string;
    next: string;
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
    // OAuth
    continueWithGoogle: string;
    or: string;
    oauthCancelled: string;
    oauthFailed: string;
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
    storytelling: {
      headline: string;
      p1: string;
      p2: string;
      p3: string;
    };
    howItWorks: {
      title: string;
      step1: {
        title: string;
        description: string;
      };
      step2: {
        title: string;
        description: string;
      };
      step3: {
        title: string;
        description: string;
      };
    };
    faq: {
      title: string;
      q1: {
        question: string;
        answer: string;
      };
      q2: {
        question: string;
        answer: string;
      };
      q3: {
        question: string;
        answer: string;
      };
      q4: {
        question: string;
        answer: string;
      };
    };
  };
  footer: {
    links: string;
    contact: string;
    email: string;
    termsOfService: string;
    privacyPolicy: string;
    copyright: string;
  };
  legal: {
    termsOfService: {
      title: string;
      seoTitle: string;
      seoDescription: string;
      intro: {
        title: string;
        content: string;
      };
      service: {
        title: string;
        content: string;
      };
      accounts: {
        title: string;
        content: string;
      };
      content: {
        title: string;
        content: string;
      };
      limitations: {
        title: string;
        content: string;
      };
      changes: {
        title: string;
        content: string;
      };
      contact: {
        title: string;
        content: string;
      };
    };
    privacyPolicy: {
      title: string;
      seoTitle: string;
      seoDescription: string;
      intro: {
        title: string;
        content: string;
      };
      dataCollection: {
        title: string;
        content: string;
      };
      encryption: {
        title: string;
        content: string;
      };
      cookies: {
        title: string;
        content: string;
      };
      rights: {
        title: string;
        content: string;
      };
      contact: {
        title: string;
        content: string;
      };
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
    errorLoading: string;
    writingPrompt: {
      title: string;
      cta: string;
    };
    featuredEntry: {
      title: string;
      daysAgo: string;
      refresh: string;
      refreshing: string;
    };
    weeklyStats: {
      streak: string;
      streakDays: string;
      thisWeek: string;
      words: string;
      bestDay: string;
    };
    prompts: string[];
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
    createError: string;
    createErrorDetails: string;
    retryCreate: string;
    zenMode: string;
    exitZenMode: string;
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
      days: string;
      noWriting: string;
      words: string;
      less: string;
      more: string;
      loadError: string;
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
      topDays: string;
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
  weekdays: {
    monday: string;
    tuesday: string;
    wednesday: string;
    thursday: string;
    friday: string;
    saturday: string;
    sunday: string;
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
  archive: {
    totalEntries: '{count} záznam',
    errorLoading: 'Chyba při načítání záznamů. Zkuste obnovit stránku.',
    page: 'Stránka {page}',
    previous: '← Předchozí',
    next: 'Další →',
  },
  meta: {
    version: 'Verze 1.0.1',
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
    // OAuth
    continueWithGoogle: 'Pokračovat přes Google',
    or: 'nebo',
    oauthCancelled: 'Přihlášení přes Google bylo zrušeno',
    oauthFailed: 'Přihlášení přes Google selhalo. Zkuste to znovu.',
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
    storytelling: {
      headline: 'Svět se zrychluje. Ty nemusíš.',
      p1: 'Celý den reaguješ na ostatní - emaily, zprávy, požadavky. Hlava plná nevyřčených myšlenek, které nemají kam jít. Kdy sis naposledy udělal 15 minut jen pro sebe?',
      p2: 'QuietPage je tvůj denní rituál. Ráno před chaosem, odpoledne na reset, nebo večer pro uzavření dne - ty si vybereš. Žádné lajky, žádní sledující, žádné soudy. Jen ty a prázdná stránka.',
      p3: 'Psaní ti pomůže zpracovat myšlenky, které by jinak zůstaly zamotané v hlavě. Není to deník. Není to blog. Je to nástroj pro tvou mentální hygienu.',
    },
    howItWorks: {
      title: 'Jak to funguje',
      step1: {
        title: 'Piš',
        description: 'Otevři QuietPage a začni psát. Nastav si vlastní denní cíl - kolik slov ti vyhovuje. Žádná pravidla, žádný formát.',
      },
      step2: {
        title: 'Sleduj',
        description: 'Aplikace zaznamenává tvé nálady, série a statistiky. Vidíš, jak se ti daří a kdy jsi nejproduktivnější.',
      },
      step3: {
        title: 'Růst',
        description: 'Časem objevíš vzorce ve svém myšlení. Psaní se stane návykem, který ti pomáhá být víc v klidu.',
      },
    },
    faq: {
      title: 'Časté otázky',
      q1: {
        question: 'Je QuietPage zdarma?',
        answer: 'Ano, QuietPage je zdarma. Stačí se zaregistrovat a můžeš začít psát.',
      },
      q2: {
        question: 'Jsou moje zápisky v bezpečí?',
        answer: 'Absolutně. Všechny zápisky jsou šifrovány. Nikdo kromě tebe je nemůže přečíst - ani my.',
      },
      q3: {
        question: 'Proč psát každý den?',
        answer: 'Pravidelnost vytváří návyk. Série (streak) tě motivuje pokračovat, i když se ti nechce.',
      },
      q4: {
        question: 'Co když den vynechám?',
        answer: 'Nic se neděje. Série se přeruší, ale můžeš začít novou. Žádné tresty, žádný tlak.',
      },
    },
  },
  footer: {
    links: 'Odkazy',
    contact: 'Kontakt',
    email: 'tomades1@gmail.com',
    termsOfService: 'Obchodní podmínky',
    privacyPolicy: 'Ochrana soukromí',
    copyright: '© {year} Tomáš Mach. Všechna práva vyhrazena.',
  },
  legal: {
    termsOfService: {
      title: 'Obchodní podmínky',
      seoTitle: 'Obchodní podmínky - QuietPage',
      seoDescription: 'Přečtěte si obchodní podmínky pro QuietPage, vaši soukromou aplikaci pro mindful psaní a deníkování.',
      intro: {
        title: 'Provozovatel služby',
        content: 'Tyto obchodní podmínky upravují používání služby QuietPage. Provozovatelem služby je Tomáš Mach, se sídlem Záryby 360, 27713, IČO: 22006401. Používáním služby souhlasíte s těmito podmínkami.',
      },
      service: {
        title: 'Popis služby',
        content: 'QuietPage je webová aplikace pro osobní psaní a reflexi. Služba umožňuje uživatelům vytvářet šifrované záznamy, sledovat své psací návyky a emocionální stav. Služba je poskytována "tak jak je" bez záruky dostupnosti.',
      },
      accounts: {
        title: 'Uživatelské účty',
        content: 'Pro používání služby je nutná registrace. Jste odpovědní za zachování důvěrnosti svého hesla a za veškerou aktivitu pod svým účtem. Zavazujete se poskytovat pravdivé informace a nepředávat přístup k účtu třetím osobám.',
      },
      content: {
        title: 'Uživatelský obsah',
        content: 'Veškerý obsah, který vytvoříte, zůstává vaším majetkem. Váš obsah je šifrován a my k němu nemáme přístup. Jste odpovědní za obsah, který vytváříte, a zavazujete se nepoužívat službu k nezákonným účelům.',
      },
      limitations: {
        title: 'Omezení odpovědnosti',
        content: 'Služba je poskytována bez jakýchkoli záruk. Neneseme odpovědnost za ztrátu dat, přerušení služby nebo jakékoli škody vzniklé používáním služby. Maximální odpovědnost je omezena na částku zaplacenou za službu.',
      },
      changes: {
        title: 'Změny podmínek',
        content: 'Vyhrazujeme si právo tyto podmínky kdykoli změnit. O významných změnách vás budeme informovat e-mailem nebo oznámením v aplikaci. Pokračováním v používání služby po změně podmínek s nimi souhlasíte.',
      },
      contact: {
        title: 'Kontakt',
        content: 'Pro dotazy ohledně těchto podmínek nás kontaktujte na tomades1@gmail.com.',
      },
    },
    privacyPolicy: {
      title: 'Ochrana soukromí',
      seoTitle: 'Ochrana soukromí - QuietPage',
      seoDescription: 'Zjistěte, jak QuietPage chrání vaše soukromí. Vaše deníkové záznamy jsou šifrovány a vaše data nikdy nesdílíme.',
      intro: {
        title: 'Závazek k ochraně soukromí',
        content: 'Vaše soukromí bereme vážně. Tyto zásady popisují, jaké údaje shromažďujeme, jak je používáme a jak je chráníme. Zavazujeme se zpracovávat vaše osobní údaje v souladu s GDPR a dalšími platnými právními předpisy.',
      },
      dataCollection: {
        title: 'Shromažďované údaje',
        content: 'Shromažďujeme pouze údaje nezbytné pro provoz služby: e-mailovou adresu pro přihlášení, vaše šifrované záznamy a základní údaje o používání (čas přihlášení, nastavení). Neshromažďujeme citlivé osobní údaje nad rámec toho, co nám sami poskytnete.',
      },
      encryption: {
        title: 'Šifrování',
        content: 'Vaše záznamy jsou šifrovány pomocí Fernet (AES-128-CBC s HMAC-SHA256). To znamená, že obsah vašich zápisků nemůžeme číst ani my jako provozovatel. Šifrovací klíč je odvozen způsobem, který zajišťuje, že pouze vy máte přístup ke svému obsahu.',
      },
      cookies: {
        title: 'Cookies',
        content: 'Používáme minimální množství cookies nezbytných pro fungování služby. Tyto cookies slouží k udržení vašeho přihlášení a zapamatování vašich preferencí (jazyk, motiv). Nepoužíváme sledovací cookies třetích stran ani analytické nástroje.',
      },
      rights: {
        title: 'Vaše práva',
        content: 'Podle GDPR máte právo na přístup ke svým údajům, jejich opravu, výmaz a přenositelnost. Můžete kdykoli požádat o export všech svých dat nebo o úplné smazání účtu. Pro uplatnění těchto práv nás kontaktujte e-mailem.',
      },
      contact: {
        title: 'Kontakt',
        content: 'Pro dotazy ohledně ochrany soukromí nebo uplatnění vašich práv nás kontaktujte na tomades1@gmail.com.',
      },
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
    errorLoading: 'Chyba při načítání dashboardu',
    writingPrompt: {
      title: 'Dnešní inspirace',
      cta: 'Začít psát',
    },
    featuredEntry: {
      title: 'Z tvé historie',
      daysAgo: 'před {{count}} dny',
      refresh: 'Zobrazit jiný',
      refreshing: 'Načítám...',
    },
    weeklyStats: {
      streak: 'Série',
      streakDays: '{{count}} dní',
      thisWeek: 'Tento týden',
      words: '{{count}} slov',
      bestDay: 'Nejlepší den',
    },
    prompts: [
      'Co tě dnes překvapilo?',
      'Popiš moment, kdy ses dnes cítil/a živě.',
      'Kdybys mohl/a změnit jednu věc na dnešku, co by to bylo?',
      'Za co jsi dnes vděčný/á?',
      'Co tě dnes rozesmálo?',
      'Jaká myšlenka se ti dnes pořád vrací?',
      'Co nového ses dnes naučil/a?',
      'Kdo ti dnes udělal radost a proč?',
      'Jaký byl nejtěžší moment dne?',
      'Co bys dělal/a, kdybys věděl/a, že nemůžeš selhat?',
      'Popiš svůj ideální den.',
      'Na co se těšíš zítra?',
      'Co tě v poslední době trápí?',
      'Jaký je tvůj největší sen?',
      'Co by sis řekl/a svému mladšímu já?',
      'Popiš místo, kde se cítíš v bezpečí.',
      'Co tě nabíjí energií?',
      'Jaké malé radosti si užíváš?',
      'Co bys chtěl/a změnit na svém životě?',
      'Popiš člověka, kterého obdivuješ.',
      'Jaký je tvůj oblíbený způsob relaxace?',
      'Co tě dělá šťastným/ou?',
      'Jaký byl tvůj nejlepší zážitek tohoto roku?',
      'Na co jsi hrdý/á?',
      'Co tě posledně inspirovalo?',
      'Jaké jsou tvé priority v životě?',
      'Popiš, jak se právě teď cítíš.',
      'Co by ses chtěl/a naučit?',
      'Jaký je tvůj vztah k času?',
      'Co tě v poslední době posunulo vpřed?',
      'Popiš svůj nejlepší přátelský vztah.',
      'Co děláš pro své zdraví?',
      'Jak vypadá tvůj ideální víkend?',
      'Co tě motivuje vstávat ráno?',
      'Jaký je tvůj největší strach?',
      'Co bys dělal/a, kdybys měl/a neomezené prostředky?',
      'Popiš své oblíbené roční období.',
      'Co tě na sobě překvapuje?',
      'Jaké knihy tě ovlivnily?',
      'Co znamená pro tebe úspěch?',
      'Popiš místo, kam by ses chtěl/a podívat.',
      'Co děláš, když potřebuješ uklidnit mysl?',
      'Jaké jsou tvé hodnoty?',
      'Co tě posledně přinutilo zamyslet se?',
      'Popiš svůj vztah k přírodě.',
      'Co bys poradil/a někomu, kdo začíná psát deník?',
      'Jak se stavíš k chybám?',
      'Co tě dělá jedinečným/ou?',
      'Jaký je tvůj oblíbený způsob trávení volného času?',
      'Na co se těšíš v budoucnosti?',
    ],
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
    createError: 'Nepodařilo se vytvořit dnešní záznam',
    createErrorDetails: 'Po {count} pokusech se nepodařilo vytvořit prázdný záznam. Zkontrolujte připojení k internetu a zkuste to znovu.',
    retryCreate: 'Zkusit znovu',
    zenMode: 'Zen mód',
    exitZenMode: 'Ukončit zen mód',
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
      encryptionInfo: 'Všechny tvé záznamy jsou šifrovány pomocí Fernet (AES-128-CBC s HMAC-SHA256).',
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
      title: 'ČETNOST PSANÍ',
      days: 'DNÍ',
      noWriting: 'Žádné psaní',
      words: 'slov',
      less: 'MÉNĚ',
      more: 'VÍCE',
      loadError: 'Nepodařilo se načíst data heatmapy',
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
      topDays: 'Top 3 Nejproduktivnější dny',
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
      title: 'SÉRIE DENNÍHO CÍLE',
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
  weekdays: {
    monday: 'pondělí',
    tuesday: 'úterý',
    wednesday: 'středa',
    thursday: 'čtvrtek',
    friday: 'pátek',
    saturday: 'sobota',
    sunday: 'neděle',
  },
};
