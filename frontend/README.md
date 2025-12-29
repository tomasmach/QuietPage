# QuietPage Frontend

React + TypeScript + Vite + Tailwind CSS frontend for QuietPage journaling application.

## Tech Stack

- **React 19** - UI library
- **TypeScript 5.9** - Type safety
- **Vite 7** - Build tool and dev server
- **Tailwind CSS 3.4** - Utility-first CSS framework
- **React Router 7** - Client-side routing
- **Lucide React** - Icon library
- **ESLint** - Code linting

## Getting Started

### Install Dependencies

```bash
npm install
```

### Development Server

```bash
npm run dev
```

Opens dev server at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

### Lint Code

```bash
npm run lint
```

## Project Structure

```
frontend/
├── src/
│   ├── App.tsx           # Main app component
│   ├── main.tsx          # App entry point
│   ├── index.css         # Global styles + Tailwind
│   └── assets/           # Static assets
├── public/               # Public static files
├── index.html            # HTML entry point
├── vite.config.ts        # Vite configuration
├── tailwind.config.js    # Tailwind configuration
├── tsconfig.json         # TypeScript configuration
└── package.json          # Dependencies
```

## Configuration

### Vite Dev Server

- Port: `5173`
- API Proxy: `/api` → `http://localhost:8000` (Django backend)

### TypeScript

- Strict mode enabled
- Path alias: `@/*` → `src/*`

### Tailwind CSS

Custom theme with CSS variables for theming:

- **Default**: Midnight (dark theme)
- **Alternative**: Paper (light theme)

Theme switching via `data-theme` attribute on root element.

### Custom CSS Classes

- `.panel` - Bordered panel component
- `.btn-primary` - Primary button with hard shadow
- `.btn-secondary` - Secondary button with hard shadow
- `.input-field` - Styled input field
- `.link-primary` - Primary link style
- `.progress-striped` - Animated progress bar

## Font

IBM Plex Mono loaded from Google Fonts (weights: 400, 500, 600, 700)

## Theme Variables

```css
:root {
  --color-bg-app: #111111;
  --color-bg-panel: #1A1A1A;
  --color-text-main: #E5E5E5;
  --color-text-muted: #888888;
  --color-border: #444444;
  --color-accent: #E5E5E5;
  --color-accent-fg: #111111;
  --color-shadow: rgba(0, 0, 0, 0.5);
}
```

## Backend Integration

API calls to Django backend are proxied through Vite dev server:

```typescript
// Example API call
fetch('/api/journal/entries/')
  .then(res => res.json())
  .then(data => console.log(data))
```

This automatically routes to `http://localhost:8000/api/journal/entries/` during development.
