# Zen Mode Design

## Overview

Zen mode provides a distraction-free writing experience by hiding the sidebar and context panel, allowing the user to focus solely on writing.

## Requirements

- Button in the editor header area (next to word count)
- Hides sidebar and context panel when active
- Keeps header with word count, progress bar, and zen mode toggle
- Textarea centered with max-width (800px) for better readability
- Auto-disables when navigating away from the page
- No keyboard shortcut (button only)

## Architecture

### State Management

Zen mode state is local to each page component (`TodayEntryPage` and `EntryEditorPage`). No new context needed since:
- State doesn't persist across navigation
- State isn't shared between pages

### Component Changes

**AppLayout.tsx**
- New prop: `zenMode?: boolean`
- When `zenMode=true`:
  - Skip rendering sidebar
  - Skip rendering context panel
  - Change grid layout to single column

**TodayEntryPage.tsx & EntryEditorPage.tsx**
- New state: `const [zenMode, setZenMode] = useState(false)`
- Pass `zenMode` prop to `AppLayout`
- Add zen mode toggle button in header section
- Textarea wrapper with conditional `max-w-3xl mx-auto` styling

**Translations**
- New keys: `editor.zenMode`, `editor.exitZenMode`

### No Changes Required

- Backend (purely frontend feature)
- Contexts (no global state needed)
- Sidebar/ContextPanel components (unchanged)

## UI Specification

### Zen Mode Button

- Location: Editor header, next to word count
- Icons: `Maximize2` (enter) / `Minimize2` (exit) from lucide-react
- Style: Ghost button matching existing header controls
- Accessibility: aria-label with localized text

### Textarea in Zen Mode

- `max-width: 800px`
- `margin: 0 auto` for centering
- Height unchanged (flex-grow fills available space)
- No additional visual changes (maintains "analog tech" aesthetic)

### Transition

- Instant toggle (no animation)
- Consistent with existing hard-edge design style

## Implementation Checklist

- [ ] Add `zenMode` prop to `AppLayout.tsx`
- [ ] Implement conditional rendering in `AppLayout.tsx`
- [ ] Add zen mode state and button to `TodayEntryPage.tsx`
- [ ] Add zen mode state and button to `EntryEditorPage.tsx`
- [ ] Add centered textarea styling for zen mode
- [ ] Add translation keys for both languages
