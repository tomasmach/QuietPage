# Zen Mode Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add distraction-free writing mode that hides sidebar and context panel while centering the textarea.

**Architecture:** Local component state in entry pages, passed as prop to AppLayout. No new contexts or backend changes needed.

**Tech Stack:** React, TypeScript, Tailwind CSS, lucide-react icons

---

## Task 1: Add Translation Keys

**Files:**
- Modify: `frontend/src/locales/cs.ts:254-269`
- Modify: `frontend/src/locales/en.ts:307-322`

**Step 1: Add translation keys to TypeScript interface**

In `frontend/src/locales/cs.ts`, add to the `entry` interface (around line 254):

```typescript
// In the Translations interface, entry section:
zenMode: string;
exitZenMode: string;
```

**Step 2: Add English translations**

In `frontend/src/locales/en.ts`, add to entry object (after `retryCreate`):

```typescript
zenMode: 'Zen mode',
exitZenMode: 'Exit zen mode',
```

**Step 3: Add Czech translations**

In `frontend/src/locales/cs.ts`, add to entry object (after `retryCreate`):

```typescript
zenMode: 'Zen mód',
exitZenMode: 'Ukončit zen mód',
```

**Step 4: Verify TypeScript compilation**

Run: `cd frontend && npm run build 2>&1 | head -20`
Expected: No TypeScript errors related to translations

**Step 5: Commit**

```bash
git add frontend/src/locales/cs.ts frontend/src/locales/en.ts
git commit -m "$(cat <<'EOF'
feat: add zen mode translation keys
EOF
)"
```

---

## Task 2: Update AppLayout Component

**Files:**
- Modify: `frontend/src/components/layout/AppLayout.tsx`

**Step 1: Add zenMode prop to interface**

Update the interface at line 5-9:

```typescript
interface AppLayoutProps {
  children: ReactNode;
  sidebar?: ReactNode;
  contextPanel?: ReactNode;
  zenMode?: boolean;
}
```

**Step 2: Destructure zenMode in component**

Update line 11:

```typescript
export function AppLayout({ children, sidebar, contextPanel, zenMode = false }: AppLayoutProps) {
```

**Step 3: Update mobile header to respect zenMode**

Wrap the mobile header div (lines 28-53) with zenMode condition. Replace:

```typescript
{/* Mobile Header with Hamburger Menu */}
<div className="lg:hidden sticky top-0 z-30 bg-bg-app border-b-2 border-border px-4 py-3 flex items-center justify-between theme-aware">
```

With:

```typescript
{/* Mobile Header with Hamburger Menu */}
{!zenMode && (
  <div className="lg:hidden sticky top-0 z-30 bg-bg-app border-b-2 border-border px-4 py-3 flex items-center justify-between theme-aware">
```

And close the conditional after the mobile header closing `</div>` (around line 53):

```typescript
  </div>
)}
```

**Step 4: Update mobile overlays to respect zenMode**

Wrap both mobile overlay sections with `!zenMode &&`:

For sidebar overlay (lines 55-85):
```typescript
{!zenMode && sidebar && isSidebarOpen && (
```

For context panel overlay (lines 87-117):
```typescript
{!zenMode && contextPanel && isContextPanelOpen && (
```

**Step 5: Update desktop grid layout**

Replace line 120:

```typescript
<div className="lg:grid lg:grid-cols-[minmax(240px,280px)_1fr_minmax(280px,320px)] lg:divide-x-2 divide-border min-h-screen">
```

With:

```typescript
<div className={
  zenMode
    ? "min-h-screen"
    : "lg:grid lg:grid-cols-[minmax(240px,280px)_1fr_minmax(280px,320px)] lg:divide-x-2 divide-border min-h-screen"
}>
```

**Step 6: Update sidebar rendering**

Replace lines 121-124:

```typescript
{/* Left Sidebar */}
<aside className="hidden lg:block sticky top-0 h-screen overflow-y-auto bg-bg-app theme-aware">
  {sidebar}
</aside>
```

With:

```typescript
{/* Left Sidebar */}
{!zenMode && (
  <aside className="hidden lg:block sticky top-0 h-screen overflow-y-auto bg-bg-app theme-aware">
    {sidebar}
  </aside>
)}
```

**Step 7: Update context panel rendering**

Replace lines 131-134:

```typescript
{/* Right Context Panel */}
<aside className="hidden lg:block sticky top-0 h-screen overflow-y-auto bg-bg-app theme-aware">
  {contextPanel}
</aside>
```

With:

```typescript
{/* Right Context Panel */}
{!zenMode && (
  <aside className="hidden lg:block sticky top-0 h-screen overflow-y-auto bg-bg-app theme-aware">
    {contextPanel}
  </aside>
)}
```

**Step 8: Verify TypeScript compilation**

Run: `cd frontend && npm run build 2>&1 | head -20`
Expected: No TypeScript errors

**Step 9: Commit**

```bash
git add frontend/src/components/layout/AppLayout.tsx
git commit -m "$(cat <<'EOF'
feat: add zenMode prop to AppLayout
EOF
)"
```

---

## Task 3: Add Zen Mode to TodayEntryPage

**Files:**
- Modify: `frontend/src/pages/TodayEntryPage.tsx`

**Step 1: Import icons**

Update line 3, add Maximize2 and Minimize2:

```typescript
import { Flame, Maximize2, Minimize2 } from 'lucide-react';
```

**Step 2: Add zenMode state**

After line 30 (`const [tags, setTags] = useState<string[]>([]);`), add:

```typescript
const [zenMode, setZenMode] = useState(false);
```

**Step 3: Pass zenMode to AppLayout**

Update the AppLayout component call around line 206. Change:

```typescript
<AppLayout
  sidebar={<Sidebar />}
  contextPanel={
```

To:

```typescript
<AppLayout
  zenMode={zenMode}
  sidebar={<Sidebar />}
  contextPanel={
```

**Step 4: Add zen mode button to header**

Find the header section (around lines 284-300) with the word count display. Update the right side div to include the zen mode button. Replace:

```typescript
<div className="text-right">
  <div className="text-4xl font-bold text-text-main">{wordCount}</div>
  <div className="text-sm font-bold uppercase text-text-text-muted">
    {t('meta.wordsToday')}
  </div>
</div>
```

With:

```typescript
<div className="flex items-end gap-4">
  <button
    onClick={() => setZenMode(!zenMode)}
    className="p-2 text-text-muted hover:text-text-main transition-colors"
    aria-label={zenMode ? t('entry.exitZenMode') : t('entry.zenMode')}
    title={zenMode ? t('entry.exitZenMode') : t('entry.zenMode')}
  >
    {zenMode ? <Minimize2 size={20} /> : <Maximize2 size={20} />}
  </button>
  <div className="text-right">
    <div className="text-4xl font-bold text-text-main">{wordCount}</div>
    <div className="text-sm font-bold uppercase text-text-text-muted">
      {t('meta.wordsToday')}
    </div>
  </div>
</div>
```

**Step 5: Add centered textarea styling in zen mode**

Find the textarea wrapper div (around line 282-283):

```typescript
<div className="p-12 bg-bg-panel flex flex-col" style={{ minHeight: 'calc(100vh - 0px)' }}>
  <div className="max-w-5xl mx-auto w-full flex flex-col flex-1">
```

Update the inner div to use conditional max-width:

```typescript
<div className="p-12 bg-bg-panel flex flex-col" style={{ minHeight: 'calc(100vh - 0px)' }}>
  <div className={`${zenMode ? 'max-w-3xl' : 'max-w-5xl'} mx-auto w-full flex flex-col flex-1`}>
```

**Step 6: Verify TypeScript compilation**

Run: `cd frontend && npm run build 2>&1 | head -20`
Expected: No TypeScript errors

**Step 7: Commit**

```bash
git add frontend/src/pages/TodayEntryPage.tsx
git commit -m "$(cat <<'EOF'
feat: add zen mode to TodayEntryPage
EOF
)"
```

---

## Task 4: Add Zen Mode to EntryEditorPage

**Files:**
- Modify: `frontend/src/pages/EntryEditorPage.tsx`

**Step 1: Import icons**

Update line 3, add Maximize2 and Minimize2:

```typescript
import { Flame, Maximize2, Minimize2 } from 'lucide-react';
```

**Step 2: Add zenMode state**

After line 30 (`const [showDeleteModal, setShowDeleteModal] = useState(false);`), add:

```typescript
const [zenMode, setZenMode] = useState(false);
```

**Step 3: Pass zenMode to AppLayout**

Update the main AppLayout component call around line 152. Change:

```typescript
<AppLayout
  sidebar={<Sidebar />}
  contextPanel={
```

To:

```typescript
<AppLayout
  zenMode={zenMode}
  sidebar={<Sidebar />}
  contextPanel={
```

**Step 4: Add zen mode button to header**

Find the header section (around lines 244-260) with the word count display. Replace:

```typescript
<div className="text-right">
  <div className="text-3xl font-bold text-text-main">{wordCount}</div>
  <div className="text-[10px] font-bold uppercase text-text-muted">
    {t('meta.wordsToday')}
  </div>
</div>
```

With:

```typescript
<div className="flex items-end gap-4">
  <button
    onClick={() => setZenMode(!zenMode)}
    className="p-2 text-text-muted hover:text-text-main transition-colors"
    aria-label={zenMode ? t('entry.exitZenMode') : t('entry.zenMode')}
    title={zenMode ? t('entry.exitZenMode') : t('entry.zenMode')}
  >
    {zenMode ? <Minimize2 size={20} /> : <Maximize2 size={20} />}
  </button>
  <div className="text-right">
    <div className="text-3xl font-bold text-text-main">{wordCount}</div>
    <div className="text-[10px] font-bold uppercase text-text-muted">
      {t('meta.wordsToday')}
    </div>
  </div>
</div>
```

**Step 5: Add centered textarea styling in zen mode**

Find the content wrapper div (around line 242-243):

```typescript
<div className="p-12 bg-bg-panel min-h-screen">
  <div className="max-w-5xl mx-auto">
```

Update the inner div:

```typescript
<div className="p-12 bg-bg-panel min-h-screen">
  <div className={`${zenMode ? 'max-w-3xl' : 'max-w-5xl'} mx-auto`}>
```

**Step 6: Verify TypeScript compilation**

Run: `cd frontend && npm run build 2>&1 | head -20`
Expected: No TypeScript errors

**Step 7: Commit**

```bash
git add frontend/src/pages/EntryEditorPage.tsx
git commit -m "$(cat <<'EOF'
feat: add zen mode to EntryEditorPage
EOF
)"
```

---

## Task 5: Manual Testing

**Step 1: Start development server**

Run: `cd frontend && npm run dev`

**Step 2: Test TodayEntryPage zen mode**

1. Navigate to http://localhost:5173/write
2. Verify zen mode button appears next to word count (Maximize2 icon)
3. Click button - sidebar and context panel should hide
4. Verify textarea is centered with narrower width
5. Verify button icon changes to Minimize2
6. Click again - UI should return to normal

**Step 3: Test EntryEditorPage zen mode**

1. Navigate to http://localhost:5173/entries/new or edit existing entry
2. Repeat same checks as above

**Step 4: Test navigation resets zen mode**

1. Enable zen mode on /write
2. Navigate to dashboard
3. Return to /write
4. Verify zen mode is OFF (reset on navigation)

**Step 5: Test mobile behavior**

1. Open DevTools, enable mobile view
2. Verify zen mode button still works
3. Verify hamburger menu is hidden in zen mode

**Step 6: Commit any fixes if needed**

---

## Task 6: Final Commit and Cleanup

**Step 1: Run full build**

Run: `cd frontend && npm run build`
Expected: Build succeeds with no errors

**Step 2: Run lint**

Run: `cd frontend && npm run lint`
Expected: No lint errors

**Step 3: Run tests**

Run: `cd frontend && npm run test:run`
Expected: All tests pass

**Step 4: Create summary commit if any additional changes were made**

If fixes were needed during testing, ensure they are committed.
