---
name: Mike Bali AI
description: Gloss cabinets for Mike, the admin, and the partner, in light and dark.
colors:
  stage-light: "#d5e6e1"
  stage-dark: "#14110e"
  ink-light: "#2e241d"
  ink-dark: "#f4f2e9"
  ink-hover-light: "#40362e"
  on-ink-light: "#f8f9f5"
  on-ink-dark: "#190f0a"
  muted-light: "#494139"
  muted-dark: "#cfcabc"
  line-light: "#7c8a82"
  line-dark: "#846e49"
  glass-solid-light: "#f4f6f0"
  madder: "#8e2f2b"
  madder-dark: "#d6857f"
  chart-green: "#4b764b"
  chart-green-deep: "#3a653b"
  chart-blue: "#397094"
  chart-blue-deep: "#215271"
  chart-blossom: "#8d5570"
  linen-shirt: "#e7cfb5"
typography:
  display:
    fontFamily: "Segoe UI, system-ui, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 600
    lineHeight: 1.1
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "Segoe UI, system-ui, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 600
    lineHeight: 1.25
    letterSpacing: "-0.015em"
  title:
    fontFamily: "Segoe UI, system-ui, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 600
    lineHeight: 1.35
    letterSpacing: "-0.01em"
  body:
    fontFamily: "Segoe UI, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "0em"
  label:
    fontFamily: "Segoe UI, system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 600
    lineHeight: 1.3
    letterSpacing: "0.01em"
rounded:
  sm: "4px"
  md: "8px"
  lg: "12px"
  pill: "999px"
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
    backgroundColor: "{colors.ink-light}"
    textColor: "{colors.on-ink-light}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: "12px 18px"
  button-secondary:
    backgroundColor: "{colors.glass-solid-light}"
    textColor: "{colors.ink-light}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: "8px 12px"
  input:
    backgroundColor: "{colors.glass-solid-light}"
    textColor: "{colors.ink-light}"
    typography: "{typography.body}"
    rounded: "{rounded.md}"
    padding: "10px 12px"
  nav-link-active:
    backgroundColor: "{colors.glass-solid-light}"
    textColor: "{colors.ink-light}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: "8px 12px"
  panel:
    backgroundColor: "{colors.glass-solid-light}"
    textColor: "{colors.ink-light}"
    typography: "{typography.body}"
    rounded: "{rounded.lg}"
    padding: "24px"
  theme-switch:
    backgroundColor: "{colors.stage-light}"
    textColor: "{colors.ink-light}"
    rounded: "{rounded.pill}"
    padding: "3px"
---

# Design System: Mike Bali AI

## 1. Overview

**Creative North Star: "Glass on the stage"**

Mike is still the guide at the gate. The interface is the gloss already shipping in the Telegram app: a tinted stage, frosted panes, a bright rim, and ink for the one filled action. Light theme is morning on a pale leaf-green stage. Dark theme is a warm night, the same materials with the values flipped.

The Telegram app, the admin, and the partner cabinet all put a day photograph under the light theme and a dusk photograph under the dark theme, then a veil, then the glass. Tables, forms, and dialogs stay on the opaque glass so a row of numbers stays readable.

The CRM cabinet has not moved. It still uses the older flat stone system. Do not treat it as part of this gloss.

This system rejects the generic slate SaaS dashboard, the luxury Bali resort brochure, the travel-blog cream and sand template, the neon beach-club promo, and the corporate real-estate CRM.

**Key Characteristics:**

- One voice for the Telegram chat, the admin, and the partner cabinet
- Two themes, chosen with a sun/moon switch and remembered on that app
- The same day and dusk photographs behind the Telegram app and both cabinets, under a veil
- Frosted panes with a 1px edge, an inset sheen, and a soft offset shadow
- Ink is the filled action, the focus ring, and the active nav item
- Chart green is a series color, never a button
- Compact 8px controls and 12px panels in the cabinets; the theme switch is the only pill there
- Short Russian labels that say what will happen

## 2. Colors

Tokens live as `oklch` in the stylesheets. The hex values below are the light and dark steps those tokens resolve to. Body text, placeholders, and large text clear WCAG 2.2 AA on both the stage and the solid glass. Component edges clear 3:1, which is why the cabinet line is a stone color rather than a white hairline: on a flat stage a white rim disappears.

### Stage

- **Stage, light** (#d5e6e1): the color under the day photograph, and the fallback before it loads. Pale leaf green. Not linen, not cream.
- **Stage, dark** (#14110e): the page at night. Warm black, not blue slate.

### Ink

- **Ink, light** (#2e241d): text, the wordmark, page titles, and the filled button. About 11.7:1 on the light stage.
- **Ink, dark** (#f4f2e9): the same roles at night. About 16.8:1 on the dark stage.
- **On ink**: the label on a filled button. Near-white on the light button, near-black on the dark button. Both pairings clear 11:1.
- **Ink hover**: the filled button pressed one step lighter in light theme, one step dimmer in dark theme.
- **Muted**: secondary text, placeholders, unselected nav. Warm, never neutral gray. About 7.7:1 on the light stage and 11.5:1 on the dark stage.

### Glass

- **Glass**: the rail and the top bar. Translucent, so the stage tints the chrome.
- **Glass strong**: panels, stat cards, partner cards, the login card.
- **Glass solid**: inputs, tables, dialogs, secondary buttons. Opaque enough that typed text and rows do not pick up the photograph.
- **Sheen**: a 1px inset highlight on the top edge of glass and of the filled button.
- **Shadow**: an offset blur under glass. Light theme is a soft green-gray at 16%. Dark theme is a deeper warm shadow.
- **Line, light** (#7c8a82): the 1px edge. About 3.3:1 on light glass.
- **Line, dark**: a warm stone edge, about 4:1 on the night pane. It is an edge, not a gold fill.

### Semantic and chart

- **Madder** (#8e2f2b in light, #d6857f in dark): error text and the error border, on a small wash of the same hue. The sentence says what failed.
- **Chart green** (#4b764b), **Chart blue** (#397094), **Chart blossom** (#8d5570), then the deeper green and blue. Series only. "Other" is #6e7276. Every slice has a text label.
- **Linen shirt** (#e7cfb5): the portrait cloth in the Telegram app. Never a page, panel, input, or button.

### Named Rules

**The Photograph Rule.** Light theme shows the day photograph. Dark theme shows the dusk photograph. A veil sits on the photograph. Tables, inputs, and dialogs use the opaque glass. The rail, the top bar, and the stat panels stay translucent so the picture remains visible.

**The Ink Action Rule.** The filled button, the focus ring, and the active nav item are ink. Chart green does not appear on a control.

**The Readable Edge Rule.** Glass keeps its sheen and its shadow. The border is dark enough to see on the flat stage. Blur is removed when `prefers-reduced-transparency: reduce` is set, and the pane becomes glass solid.

## 3. Typography

**Face:** Segoe UI, then system-ui, then sans-serif. One family for the wordmark, titles, labels, tables, and body. The face must cover Cyrillic.

### Hierarchy

- **Wordmark** (600, 1.25rem, line-height 1.1, tracking -0.02em): MIKE, then BALI GUIDE under it at 0.75rem, weight 600, tracking 0.08em.
- **Headline** (600, 1.5rem, line-height 1.25, tracking -0.015em): the one title on a screen. `text-wrap: balance`.
- **Title** (600, 1.125rem, line-height 1.35, tracking -0.01em): panel titles and dialog titles.
- **Body** (400, 1rem, line-height 1.5): table cells and help. `text-wrap: pretty` on paragraphs.
- **Label** (600, 0.875rem, line-height 1.3, tracking 0.01em): buttons, nav, field labels. Sentence case.

### Named Rules

**The One Face Rule.** Segoe UI carries the wordmark, the page title, and the UI.

**The Logo Lockup Rule.** The only all-caps setting is the wordmark: MIKE, then BALI GUIDE. No tracked uppercase eyebrow above a section.

## 4. Elevation and theme

Depth is the glass: translucent fill, 1px line, inset sheen, and a shadow with offset and blur (`0 10px 28px` on panes, `0 16px 40px` on dialogs). Hover does not add a second shadow.

The theme switch is a 76×36 pill, sun then moon, `aria-pressed` on the chosen side. It sits in the cabinet top bar beside «Выйти», and at the top of the login card. Each app stores its own choice (`mike-bali-admin-theme`, `mike-bali-partner-theme`, `mike-bali-tma-theme`). The first visit follows the system.

Motion is a state change of background, border, and color, about 160–180ms, ease-out. No entrance choreography. Under `prefers-reduced-motion: reduce`, those transitions are removed.

### Focus

`outline: 2px solid` ink, offset 2px. The ring is the same ink as the text, in both themes.

## 5. Components

Cabinet corners stay compact: 8px on controls, 12px on panels, 4px on chart swatches. The theme switch is the only pill. The Telegram app may keep its own pill buttons; do not import those radii into a table.

### Buttons

- **Primary:** ink fill, on-ink text, label type, padding 12px 18px, inset sheen. Hover uses ink hover. Disabled is glass solid with muted text, no opacity fade.
- **Secondary:** glass solid, ink text, 1px line, padding 8px 12px. Hover uses the hover wash. «Выйти» and cancel.
- **Text:** ink, underlined. Danger text is madder.

### Panels

A panel holds one job: a form, a table, a stat with its legend. 12px radius, glass strong, 1px line, sheen, shadow. Tables and dialogs use glass solid. Dialogs sit on a scrim. No colored side stripe.

### Inputs

Glass solid, 1px line, 8px radius, padding 10px 12px, inset sheen. The label sits above the field. Placeholder is muted. Focus turns the border to ink and draws the focus ring. Errors use a madder border and a madder sentence.

### Navigation

Admin: a left rail, 13rem, glass, 1px line on the right. The wordmark sits at the top in ink. Links are label type, muted, 8px radius. Hover uses the hover wash. The active link is an ink chip with on-ink text, the same pairing as the filled button, so the section stays obvious on a light rail and on a dark one.

Below 960px the rail becomes a horizontal bar and the links wrap.

The top bar holds the theme switch and «Выйти». It does not repeat the page title.

Partner: a top bar only. The wordmark is on the start side. The switch and «Выйти» are on the end side. The page is statistics.

### Charts

A donut plus a legend. Series order: chart green, chart blue, chart blossom, deep green, deep blue. Other is #6e7276. Slice gaps are 1px of glass solid. Every slice has a text label and a number. Empty copy is «Пока нет данных».

### Wordmark

Two split gate prongs, then MIKE / BALI GUIDE, in ink. Once in the rail or the partner bar, and on the login card. Not a pattern and not a bullet.

## 6. Do's and Don'ts

### Do:

- **Do** set the cabinet page to the stage color for the active theme.
- **Do** use ink for the filled button, the focus ring, the wordmark, and the active nav item.
- **Do** keep tables and inputs on glass solid.
- **Do** keep cabinet controls at 8px and panels at 12px.
- **Do** remember the theme per app, and follow the system until a person chooses.
- **Do** write button labels as a verb plus an object, in Russian, sentence case.
- **Do** pair every chart color with a text legend.
- **Do** drop blur under `prefers-reduced-transparency: reduce`, and drop color transitions under `prefers-reduced-motion: reduce`.

### Don't:

- **Don't** leave the cabinet on a flat color when the day or dusk photograph is available.
- **Don't** build the generic slate SaaS dashboard.
- **Don't** use linen, cream, or sand as a background. Linen stays in the portrait.
- **Don't** use neon chart series: no cyan, magenta, or purple.
- **Don't** use chart green as a button, a link, or the focus ring.
- **Don't** make cabinet buttons into pills. The theme switch is the exception.
- **Don't** carry meaning by color alone. Errors need a sentence. Charts need a legend.
- **Don't** animate layout, bounce, or reveal content by hiding it until a class is added.
- **Don't** restyle the CRM cabinet as part of this system until that cabinet is deliberately moved.
