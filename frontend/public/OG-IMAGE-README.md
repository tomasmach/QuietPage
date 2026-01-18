# OG Image Setup

## Current Status

The repository contains:
- `og-image.svg` - Source SVG design (1200x630)
- `og-image-generator.html` - HTML template for generating PNG

## Production Setup Required

To complete the OG image setup for social media sharing:

### Option 1: Convert SVG to PNG (Recommended)

Using ImageMagick:
```bash
convert og-image.svg -resize 1200x630 og-image.png
```

Using Inkscape:
```bash
inkscape og-image.svg --export-filename=og-image.png --export-width=1200 --export-height=630
```

### Option 2: Generate from HTML Template

Using Puppeteer (Node.js):
```javascript
const puppeteer = require('puppeteer');
const browser = await puppeteer.launch();
const page = await browser.newPage();
await page.setViewport({ width: 1200, height: 630 });
await page.goto(`file://${__dirname}/og-image-generator.html`);
await page.screenshot({ path: 'og-image.png' });
await browser.close();
```

### Option 3: Use Online Tool

1. Open `og-image-generator.html` in browser
2. Use browser screenshot tool (1200x630 viewport)
3. Save as `og-image.png` in this directory

## Verification

After creating `og-image.png`, verify:
1. File exists at `frontend/public/og-image.png`
2. Dimensions are exactly 1200x630 pixels
3. File size is under 1MB (ideally under 300KB)
4. Test social media preview using https://www.opengraph.xyz/

## Meta Tags

The following files reference `/og-image.png`:
- `frontend/index.html` (fallback meta tags)
- `frontend/src/components/SEO.tsx` (dynamic meta tags)
