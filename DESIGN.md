---
name: Mike Bali AI
description: A daylight guide system for Mike, the admin, and the partner cabinet.
colors:
  chalk: "#ffffff"
  temple-stone: "#2b2e32"
  temple-stone-hover: "#44484c"
  fresh-green: "#4b764b"
  fresh-green-hover: "#3a653b"
  linen-shirt: "#e7cfb5"
  warung-paper: "#f3f5f6"
  surface: "#fafbfc"
  terrace-ink: "#222427"
  gate-muted: "#44484c"
  gate-line: "#6e7276"
  terrace-wash: "#e7eaec"
  madder: "#8e2f2b"
  chart-ash: "#51565b"
  chart-mist: "#8a9096"
typography:
  display:
    fontFamily: "Fraunces, Iowan Old Style, Palatino, serif"
    fontSize: "clamp(2rem, 3vw, 2.75rem)"
    fontWeight: 560
    lineHeight: 1.15
    letterSpacing: "-0.02em"
    fontVariation: "'opsz' 48, 'SOFT' 20, 'WONK' 0"
  headline:
    fontFamily: "Fraunces, Iowan Old Style, Palatino, serif"
    fontSize: "1.5rem"
    fontWeight: 560
    lineHeight: 1.25
    letterSpacing: "-0.015em"
    fontVariation: "'opsz' 36, 'SOFT' 20, 'WONK' 0"
  title:
    fontFamily: "Golos Text, system-ui, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 600
    lineHeight: 1.35
    letterSpacing: "-0.01em"
  body:
    fontFamily: "Golos Text, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "0em"
  label:
    fontFamily: "Golos Text, system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 600
    lineHeight: 1.3
    letterSpacing: "0.01em"
rounded:
  sm: "4px"
  md: "8px"
  lg: "12px"
spacing:
  2xs: "4px"
  xs: "8px"
  sm: "12px"
  md: "16px"
  lg: "24px"
  xl: "40px"
  2xl: "64px"
components:
  button-primary:
    backgroundColor: "{colors.fresh-green}"
    textColor: "{colors.chalk}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: "12px 18px"
  button-primary-hover:
    backgroundColor: "{colors.fresh-green-hover}"
    textColor: "{colors.chalk}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: "12px 18px"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.terrace-ink}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: "8px 12px"
  button-secondary-hover:
    backgroundColor: "{colors.terrace-wash}"
    textColor: "{colors.terrace-ink}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: "8px 12px"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.terrace-ink}"
    typography: "{typography.body}"
    rounded: "{rounded.md}"
    padding: "10px 12px"
  input-focus:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.terrace-ink}"
    typography: "{typography.body}"
    rounded: "{rounded.md}"
    padding: "10px 12px"
  nav-link:
    backgroundColor: "{colors.warung-paper}"
    textColor: "{colors.gate-muted}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: "8px 12px"
  nav-link-active:
    backgroundColor: "{colors.terrace-wash}"
    textColor: "{colors.fresh-green}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: "8px 12px"
  chip:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.terrace-ink}"
    typography: "{typography.label}"
    rounded: "{rounded.sm}"
    padding: "4px 8px"
  chip-selected:
    backgroundColor: "{colors.terrace-wash}"
    textColor: "{colors.fresh-green}"
    typography: "{typography.label}"
    rounded: "{rounded.sm}"
    padding: "4px 8px"
  panel:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.terrace-ink}"
    typography: "{typography.body}"
    rounded: "{rounded.lg}"
    padding: "24px"
  wordmark:
    backgroundColor: "{colors.warung-paper}"
    textColor: "{colors.temple-stone}"
    padding: "0px"
---

# Design System: Mike Bali AI

## 1. Overview

**Creative North Star: "The Guide at the Gate"**

Mike is still the guide at the gate, already talking. The interface should feel like that meeting in daylight: dark volcanic stone, and one bright leaf. Density is a working cabinet, not a campaign page. Type does the hospitality. Color is the gate: temple stone for the name and the page, fresh green for the action.

The ground is shade on stone, not the shirt. A tourist reads this on a phone. An admin reads it at a desk. Both need a light field with real contrast. The page is neutral stone grey. It is never linen, cream, sand, or a green wash.

This system rejects the generic slate SaaS dashboard (Segoe UI, gray panels), the luxury Bali resort brochure (gold serif, infinity pool, barefoot-luxury copy), the travel-blog cream and sand template, the neon beach-club / nightlife promo, and the corporate real-estate CRM.

**Key Characteristics:**

- One voice for the Telegram chat, the admin, and the partner cabinet
- Neutral stone paper; the linen shirt stays in the portrait and never becomes a background
- Temple stone carries the name; fresh green is the one filled action; no gold or rust fills
- Flat surfaces, a 1px stone line, a shadow only under a dialog
- Fraunces for the stitched name and page titles; Golos Text for everything said
- Short Russian labels that say what will happen

## 2. Colors

The palette is temple stone plus one fresh green, corrected for WCAG 2.2 AA. Dark grey is the gate, the way a Bali candi reads in shade: charcoal, not blue, not sand. Fresh green is the leaf against that stone. It is the filled action, the selected nav item, the focus ring, and the lead count.

### Primary

- **Fresh Green** (#4b764b): the reference green. Filled buttons, the focus ring, the "on" state, and the lead count. White label text on this green is about 5.3:1. As text on the page it is about 4.8:1.
- **Fresh Green Hover** (#3a653b): the same green pressed darker. White text is about 6.8:1. Selected nav labels use this step, because the reference green on the wash is about 4.4:1 and this step is about 5.6:1.

### Stone

- **Temple Stone** (#2b2e32): the wordmark and page titles. Dark grey, like dry andesite in shade. About 12.5:1 on the page.
- **Temple Stone Hover** (#44484c): a lifted stone for quiet text that needs a hover, when that control is not the green action.

### Neutral

- **Warung Paper** (#f3f5f6): the page. A neutral stone grey, chroma near zero. Body backgrounds, the nav rail, the login field. Not green, not cream, not sand.
- **Surface** (#fafbfc): panels, inputs, dialogs, and secondary buttons. One step lighter than the page, so a list sits on the paper without a drop shadow.
- **Chalk** (#ffffff): text on fresh green and madder.
- **Terrace Ink** (#222427): body text and sans headings. About 14:1 on warung paper.
- **Gate Muted** (#44484c): secondary text, placeholders, and unselected nav. About 8.4:1 on warung paper.
- **Gate Line** (#6e7276): 1px borders on panels, inputs, tables, and the nav rail. About 4.4:1 on warung paper, so the edge is visible.
- **Terrace Wash** (#e7eaec): the active nav row, the selected chip, and the hover of a secondary button.
- **Linen Shirt** (#e7cfb5): the portrait cloth. Reference only. See the rule below.
- **Madder** (#8e2f2b): errors. White text on madder is about 7.4:1. The wash behind an error is #f4ecec, a small cool field, never the page.
- **Chart Ash** (#51565b) and **Chart Mist** (#8a9096): extra chart slices with temple stone and fresh green. A chart still needs a text legend.

### Named Rules

**The Not-the-Shirt Rule.** Linen Shirt (#e7cfb5) is the portrait. It is never a page, panel, input, or button fill. Sand, cream, and beige are the same mistake. A green-tinted page is the old palette. The page stays Warung Paper.

**The One Leaf Rule.** Fresh green is the only saturated color. It fills the one action button, marks the current section, and colors the lead count. The wordmark and the page stay stone. Two filled buttons in one row are prohibited.

**The No Gold Rule.** No gold type, no gold buttons, no gold rules, no rust fills, no gold page.

## 3. Typography

**Display Font:** Fraunces (with Iowan Old Style, Palatino)
**Body Font:** Golos Text (with system-ui)
**Label Font:** Golos Text

**Character:** Fraunces is the stitch: a sturdy old-style serif with the softness turned down, used where the shirt carries a word. Golos Text is the conversation: a plain Cyrillic grotesque for tables, forms, and buttons. Both cover Russian. The pairing is a handmade name next to a spoken sentence. It is not a fashion serif, and it is not Segoe UI.

Load Fraunces as a variable font with Cyrillic, `WONK` 0 and `SOFT` 20. Use weight 560 where the variable axis is available, and 600 on a static cut. Load Golos Text with Cyrillic at 400 and 600.

### Hierarchy

- **Display** (560, clamp(2rem, 3vw, 2.75rem), line-height 1.15, tracking -0.02em): the wordmark and a rare page title. Ceiling stays at 2.75rem. This is a cabinet, not a poster.
- **Headline** (560, 1.5rem, line-height 1.25, tracking -0.015em): the one title on a screen, such as "Вход" or "Статистика". `text-wrap: balance`.
- **Title** (600, 1.125rem, line-height 1.35, tracking -0.01em): panel titles and dialog titles, in Golos Text.
- **Body** (400, 1rem, line-height 1.5): answers, table cells, help text. Measure stays within 65 to 75 characters. `text-wrap: pretty` on paragraphs.
- **Label** (600, 0.875rem, line-height 1.3, tracking 0.01em): buttons, nav, field labels, chips. Sentence case.

### Named Rules

**The Stitch and Speech Rule.** Fraunces is the embroidery: the wordmark and page titles. Golos Text is the conversation: labels, tables, buttons, and body. Reversing them is prohibited.

**The Logo Lockup Rule.** The only all-caps setting is the wordmark: MIKE, then BALI GUIDE. Section titles, buttons, and nav are sentence case. No tracked uppercase eyebrow above a section.

**The Straight Stitch Rule.** Fraunces ships with wonk at 0 and softness at 20. A high-contrast fashion serif, a script, or a gold headline is the luxury brochure, and it is out.

## 4. Elevation

Depth is tonal. The page is warung paper. Panels and inputs are surface, separated by a 1px gate line. Nothing lifts because it is a card. The portrait's gate is a stone edge in daylight, so the UI edge is a line, not a glow.

Dialogs are the exception. A dialog is a surface panel with a short ink-tinted shadow, enough to say it sits over the page. Menus use the same shadow. Hover does not add a shadow.

Motion is a state change: background, border, and color in 160ms with cubic-bezier(0.25, 1, 0.5, 1). No entrance choreography, no bounce. Under `prefers-reduced-motion: reduce`, those transitions are removed.

### Shadow Vocabulary

- **Dialog** (`box-shadow: 0 12px 32px rgb(34 36 39 / 0.14)`): modal forms and menus only. The tint is terrace ink, so the lift stays stone grey.
- **Focus** (`outline: 2px solid #4b764b; outline-offset: 2px`): every interactive control. The ring is fresh green on the page, visible without a glow.

### Named Rules

**The Flat Gate Rule.** Surfaces are flat. Depth is a 1px gate line (#6e7276). A shadow appears only under a dialog or a menu. If the shadow looks like a 2014 app, it is too dark and too tight: lighten it toward terrace ink at 14% and keep the blur at 32px.

## 5. Components

Controls are compact enough for a cabinet and large enough for a phone outdoors. Corners are lightly cut (8px on controls, 12px on panels, 4px on chips). Pills, full-bleed gradients, and side stripes are out.

### Buttons

Plain and pressed, like a shirt that has been worn in. One filled action per view.

- **Shape:** lightly cut corners (8px).
- **Primary:** Fresh green fill, chalk text, label type, padding 12px 18px. Hover shifts to Fresh Green Hover. This is the one filled action: enter, save, and the control that contacts a person or opens a place.
- **Secondary:** Surface fill, terrace ink text, 1px gate line, padding 8px 12px. Hover fills with terrace wash. Use for "Выйти" and for cancel.
- **Focus:** 2px fresh green outline, 2px offset.
- **Disabled:** terrace wash fill, gate muted text, gate line border. No opacity fade. The label still clears 4.5:1.

### Chips

Partner types and filters. A chip is a choice, not a decoration.

- **Style:** surface fill, terrace ink text, 1px gate line, 4px radius, padding 4px 8px, label type.
- **Selected:** terrace wash fill, fresh green hover text, 1px fresh green border.
- **State:** the selected chip is also exposed to assistive tech with `aria-pressed` or a real radio. Color is not the only signal.

### Cards / Containers

Panels, not card grids. A panel holds one job: a form, a table, a stat with its legend.

- **Corner style:** 12px.
- **Background:** surface on warung paper.
- **Shadow strategy:** none at rest. Dialogs use the dialog shadow from Elevation.
- **Border:** 1px gate line on all sides. No colored side stripe.
- **Internal padding:** 24px. Inside a dialog, the title is a Golos Text title, then 16px, then the fields.

### Inputs / Fields

- **Style:** surface fill, 1px gate line, 8px radius, padding 10px 12px, body type, terrace ink text. The label sits above the field in label type, sentence case, 4px gap.
- **Placeholder:** gate muted (#44484c). Same contrast bar as body text.
- **Focus:** border becomes 1px fresh green, plus the 2px focus outline. No glow.
- **Error:** 1px madder border, and a madder message under the field in body type. The message says what to fix. The border is not the only signal.
- **Disabled:** terrace wash fill, gate muted text.

### Navigation

A left rail, 208px, warung paper, 1px gate line on the right. The wordmark sits at the top of the rail, in temple stone. Links are label type, sentence case, gate muted, with 8px 12px padding and 8px radius. Hover uses terrace wash. The active link is terrace wash with the darker fresh green, so the label stays readable on the wash.

Below 960px the rail becomes a horizontal bar under the wordmark. Links wrap. The active link stays the darker fresh green on wash, so the section is obvious without a hamburger mystery.

The header on the cabinet only holds the secondary "Выйти" button, aligned to the end. It does not repeat the page title.

### Charts

Stats are a donut plus a legend, never a naked rainbow. Series order is fixed: Fresh Green, Temple Stone, Chart Ash, Gate Line, Chart Mist. "Other" uses Gate Muted.

- **Shape:** the ring is a stroke, not a gradient. Slice gaps are 1px of surface.
- **Legend:** every slice has a text label and a number beside a 10px swatch. The swatch is `aria-hidden`. Color is never the only label.
- **Empty:** one sentence in body type, gate muted: "Пока нет данных". No illustration.

### Wordmark

The signature. A two-prong candi, then the lockup, in temple stone.

- **Mark:** two split gate prongs, 28px wide, current color. It appears once, at the top of the nav or on the login screen. It is not a repeating pattern, a background, or a bullet.
- **Name:** MIKE in Fraunces, about 1.25rem, weight 560, tracking -0.02em.
- **Role:** BALI GUIDE in Golos Text, 0.75rem, weight 600, tracking 0.08em, under the name. This is the logo, not a section eyebrow.

## 6. Do's and Don'ts

### Do:

- **Do** set the page to Warung Paper (#f3f5f6) and body text to Terrace Ink (#222427). Never linen, cream, sand, or a green page wash.
- **Do** use Temple Stone (#2b2e32) for the wordmark and page titles.
- **Do** use Fresh Green (#4b764b) for the filled button, the active nav item, the focus ring, and the lead count.
- **Do** keep panels flat, with a 1px Gate Line (#6e7276) and 24px padding.
- **Do** set Fraunces on the wordmark and page titles, and Golos Text on labels, tables, buttons, and body. Both with Cyrillic.
- **Do** write button labels as a verb plus an object, in Russian, sentence case: "Сохранить партнёра", "Открыть карту".
- **Do** pair every chart color with a text legend.
- **Do** remove color and shadow transitions when `prefers-reduced-motion: reduce` is set.

### Don't:

- **Don't** build the generic slate SaaS dashboard (Segoe UI, gray panels). No slate palette, no default sans as the brand face, no gray-on-gray tables.
- **Don't** drift into a luxury Bali resort brochure: gold serif, infinity pool, barefoot-luxury copy. No gold fill anywhere.
- **Don't** use the travel-blog cream and sand template. Linen Shirt (#e7cfb5) is never a background.
- **Don't** use a neon beach-club / nightlife promo: no cyan, magenta, or purple chart series, no glow, no glass.
- **Don't** look like a corporate real-estate CRM: no dense gray grids, no tiny uppercase headers, no side-stripe alerts.
- **Don't** put two filled buttons in one row, or use rust, gold, or a second green for text or fills.
- **Don't** carry meaning by color alone. Errors need a sentence. Charts need a legend. Selected chips need a state.
- **Don't** animate layout, bounce, or reveal content by hiding it until a class is added.
