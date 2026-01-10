# QUIETPAGE DESIGN SYSTEM
> **Role:** Frontend Rules & Style Guide
> **Framework:** React + Tailwind CSS
> **Design Philosophy:** "Analog Tech" / "Raw Architect"
> **Themes:** Midnight (Priority) & Paper

---

## 1. CORE PHILOSOPHY
QuietPage is a writing tool for focus. It is NOT a generic SaaS.
- **Vibe:** Technical, raw, precise, distraction-free.
- **Metaphor:** An architect's drafting table or a terminal in a dark room.
- **Key Element:** "Hard" aesthetics (sharp borders, hard shadows, monospace).
- **Avoid:** Round buttons, soft gradients, blur effects, standard "corporate" blue.

---

## 2. THEME CONFIGURATION (Tailwind)

Use CSS variables for theming to allow instant switching between `Midnight` and `Paper`.

### `tailwind.config.js` extension:
```javascript
theme: {
  extend: {
    fontFamily: {
      mono: ['"IBM Plex Mono"', 'monospace'], // PRIMARY FONT FOR EVERYTHING
    },
    colors: {
      // Semantic colors mapped to CSS variables
      bg: {
        app: 'var(--color-bg-app)',      // Main background
        panel: 'var(--color-bg-panel)',  // Sidebar/Widget background
      },
      text: {
        main: 'var(--color-text-main)',  // Primary text
        muted: 'var(--color-text-muted)',// Secondary/Meta text
      },
      border: {
        DEFAULT: 'var(--color-border)',  // Main border color
      },
      accent: {
        DEFAULT: 'var(--color-accent)',  // Interactive elements active state
        fg: 'var(--color-accent-fg)',    // Text on accent bg
      }
    },
    boxShadow: {
      'hard': '4px 4px 0px 0px var(--color-shadow)', // THE SIGNATURE SHADOW
    },
    backgroundImage: {
      'striped': 'linear-gradient(45deg, rgba(255,255,255,0.15) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0.15) 75%, transparent 75%, transparent)',
    }
  }
}
```

### CSS Variables (`index.css`):

**DEFAULT (Midnight Mode) - PRIORITY:**
```css
:root {
  /* Midnight (Dark, Calm, High Contrast) */
  --color-bg-app: #1A1A1A;
  --color-bg-panel: #2D2D2D;
  --color-text-main: #F5F5F5;
  --color-text-muted: #999999;
  --color-border: #F5F5F5;
  --color-accent: #F5F5F5;
  --color-accent-fg: #1A1A1A;
  --color-shadow: #F5F5F5;
}

/* Paper Theme (Light, Ink, Raw) */
[data-theme='paper'] {
  --color-bg-app: #FFFCF5;
  --color-bg-panel: #FFFFFF;
  --color-text-main: #1A1A1A;
  --color-text-muted: #666666;
  --color-border: #1A1A1A;
  --color-accent: #1A1A1A;
  --color-accent-fg: #FFFFFF;
  --color-shadow: rgba(0, 0, 0, 1);
}
```

---

## 3. LAYOUT: "The Architect"

The application uses a strict 3-column layout. Borders are explicit.

- **Structure:** `Grid: [240px Sidebar] [1fr Main Content] [280px Context Panel]`
- **Separation:** Columns are separated by `border-r-2` (right border) using `border-border`.
- **Scrolling:**
  - Sidebars have independent scrolling if needed.
  - Main Content has independent scrolling.
  - `body` is `overflow: hidden`.

---

## 4. UI COMPONENTS

### A. Typography
- **Font:** ALWAYS `IBM Plex Mono`.
- **Headers:** Uppercase, bold, tracking-widest (e.g., `text-xs font-bold uppercase tracking-widest`).
- **Body:** Relaxed line-height (`leading-relaxed`), typically `text-lg` for writing.

### B. Buttons & Interactive Elements
- **Shape:** Sharp corners or very minimal radius (`rounded-none` or `rounded-sm`).
- **Borders:** Visible borders (`border-2`).
- **Hover:**
  - Hard Shadow effect: `shadow-hard`
  - OR Invert colors (bg becomes fg).
  - OR Translate: `translate-x-[2px] translate-y-[2px]` (tactile feel).

### C. Progress Bar (The "750 Words" Metric)
- **Style:** "Railway" style.
- **Container:** Bordered (`border-2`), transparent or panel-bg.
- **Fill:** Solid color + Striped Animation.
- **Animation CSS:**
  ```css
  @keyframes stripe-slide {
    0% { background-position: 0 0; }
    100% { background-position: 20px 20px; }
  }
  .animate-stripe {
    background-size: 20px 20px;
    animation: stripe-slide 2s linear infinite;
  }
  ```

### D. Cards / Badges
- **Border:** `border-2 border-border`.
- **Background:** `bg-bg-panel`.
- **Shadow:** `shadow-hard`.
- **Padding:** Generous (`p-6`).

### E. Inputs (Writing Area)
- **Appearance:** Invisible / Seamless.
- **Focus:** No outline, maybe a subtle blinking block cursor.
- **Placeholder:** Low opacity `text-text-muted`.

---

## 5. ANIMATIONS
- **Transitions:** `transition-all duration-300 ease-in-out` (for theme switching).
- **Interactions:** Fast, snappy (`duration-150`) for button hovers.
- **Loading:** Simple blinking block (terminal cursor style), no spinning circles.

---

## 6. ICONS
- **Library:** Lucide React.
- **Style:** Stroke width `2px`.
- **Size:** Typically `20px` (small) or `18px`.
- **Behavior:** Often used inside square buttons with borders.

---

## 7. SEMANTIC COLORS

The brutalist philosophy (no gradients, no soft effects) applies consistently across the entire application.

### Status & Semantic Colors:
- **Success/warning/error:** Use semantic colors (green/amber/red) when needed for status indicators
- **Time-of-day indicators:** Morning/afternoon/evening may use contextual warm/cool tones if they represent temporal data
- **Always maintain:** Hard borders, sharp corners, solid colors (no gradients), no blur effects

---

## 8. IMPLEMENTATION CHECKLIST
1. [ ] Install `lucide-react`.
2. [ ] Add `IBM Plex Mono` via Google Fonts.
3. [ ] Set up CSS variables for `Midnight` (default) and `Paper`.
4. [ ] Configure `tailwind.config.js` with the extend block above.
5. [ ] Build the 3-column Grid Layout.
6. [ ] Implement the Theme Toggler (class switching on `html` or `body`).
