# Landing Page & Legal Pages Design

## Overview

Enhance QuietPage landing page with storytelling, FAQ, footer, legal pages, and comprehensive SEO.

## Operator

- **Business name:** Tomáš Mach
- **Address:** Záryby 360, 27713
- **IČO:** 22006401
- **Email:** tomades1@gmail.com

---

## Landing Page Structure

### 1. Hero (existing, minor updates)
Keep current hero with headline, subheadline, and CTAs.

### 2. Storytelling Section (new)

**Czech:**
> **Svět se zrychluje. Ty nemusíš.**
>
> Celý den reaguješ na ostatní - emaily, zprávy, požadavky. Hlava plná nevyřčených myšlenek, které nemají kam jít. Kdy sis naposledy udělal 15 minut jen pro sebe?
>
> QuietPage je tvůj denní rituál. Ráno před chaosem, odpoledne na reset, nebo večer pro uzavření dne - ty si vybereš. Žádné lajky, žádní sledující, žádné soudy. Jen ty a prázdná stránka.
>
> Psaní ti pomůže zpracovat myšlenky, které by jinak zůstaly zamotané v hlavě. Není to deník. Není to blog. Je to nástroj pro tvou mentální hygienu.

**English:**
> **The world speeds up. You don't have to.**
>
> All day you react to others - emails, messages, demands. A head full of unspoken thoughts with nowhere to go. When did you last take 15 minutes just for yourself?
>
> QuietPage is your daily ritual. Morning before the chaos, afternoon for a reset, or evening to close the day - you choose. No likes, no followers, no judgment. Just you and a blank page.
>
> Writing helps you process thoughts that would otherwise stay tangled. It's not a diary. It's not a blog. It's a tool for your mental hygiene.

### 3. Features Section (existing)
Keep current 4 feature cards (Privacy, Mood Tracking, Streaks, Insights).

### 4. How It Works Section (new)

**Czech:**
1. **Piš** - Otevři QuietPage a začni psát. Nastav si vlastní denní cíl - kolik slov ti vyhovuje. Žádná pravidla, žádný formát.
2. **Sleduj** - Aplikace zaznamenává tvé nálady, série a statistiky. Vidíš, jak se ti daří a kdy jsi nejproduktivnější.
3. **Růst** - Časem objevíš vzorce ve svém myšlení. Psaní se stane návykem, který ti pomáhá být víc v klidu.

**English:**
1. **Write** - Open QuietPage and start writing. Set your own daily goal - whatever word count works for you. No rules, no format.
2. **Track** - The app records your moods, streaks, and stats. See how you're doing and when you're most productive.
3. **Grow** - Over time, you'll discover patterns in your thinking. Writing becomes a habit that helps you stay calm.

### 5. FAQ Section (new)

**Czech:**
- **Je QuietPage zdarma?** - Ano, QuietPage je zdarma. Stačí se zaregistrovat a můžeš začít psát.
- **Jsou moje zápisky v bezpečí?** - Absolutně. Všechny zápisky jsou šifrovány. Nikdo kromě tebe je nemůže přečíst - ani my.
- **Proč psát každý den?** - Pravidelnost vytváří návyk. Série (streak) tě motivuje pokračovat, i když se ti nechce.
- **Co když den vynechám?** - Nic se neděje. Série se přeruší, ale můžeš začít novou. Žádné tresty, žádný tlak.

**English:**
- **Is QuietPage free?** - Yes, QuietPage is free. Just sign up and start writing.
- **Are my entries secure?** - Absolutely. All entries are encrypted. No one can read them except you - not even us.
- **Why write every day?** - Consistency builds habit. Streaks motivate you to keep going, even when you don't feel like it.
- **What if I skip a day?** - Nothing happens. Your streak resets, but you can start a new one. No penalties, no pressure.

### 6. Final CTA (existing)
Keep current CTA section.

### 7. Footer (new)

Layout:
```
─────────────────────────────────────────────────────────
[Logo QuietPage]     [Odkazy]              [Kontakt]
                     Terms of Service      tomades1@gmail.com
                     Privacy Policy
─────────────────────────────────────────────────────────
                   © 2025 Tomáš Mach
```

- Links to `/terms` and `/privacy`
- Copyright: `© 2025 Tomáš Mach. Všechna práva vyhrazena.` / `© 2025 Tomáš Mach. All rights reserved.`

---

## Legal Pages

### Terms of Service (`/terms`)
- Bilingual (CS/EN)
- Operator info, service description, user responsibilities, limitations

### Privacy Policy (`/privacy`)
- Bilingual (CS/EN)
- Data collection, encryption, cookies, user rights (GDPR)

---

## SEO Implementation

### Technical SEO
- Meta tags (title, description) per page
- Open Graph tags (og:title, og:description, og:image, og:url)
- Twitter Card tags
- Structured data (JSON-LD) - WebApplication schema
- sitemap.xml
- robots.txt
- Canonical URLs

### OG Image
- Static image for social sharing (1200x630px)
- QuietPage branding with tagline

### Content SEO
- Optimized headlines and copy on landing page
- Semantic HTML structure (proper heading hierarchy)

---

## Implementation Tasks

1. Update landing page with new sections (Storytelling, How It Works, FAQ)
2. Create Footer component
3. Create Terms of Service page (bilingual)
4. Create Privacy Policy page (bilingual)
5. Add routes for `/terms` and `/privacy`
6. Update translations (cs.ts, en.ts)
7. Implement SEO (meta tags, OG, structured data)
8. Create OG image
9. Add sitemap.xml and robots.txt
