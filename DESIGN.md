---
name: Mike Bali AI
description: A daylight guide system for Mike, the admin, and the partner cabinet.
colors:
  chalk: "#ffffff"
  temple-green: "#2c4030"
  temple-green-hover: "#3e5342"
  embroidery-rust: "#8a4520"
  embroidery-rust-hover: "#6e3416"
  embroidery-thread: "#b46432"
  thread-gold: "#a07846"
  linen-shirt: "#e7cfb5"
  warung-paper: "#f3f8f4"
  surface: "#fcfefc"
  terrace-ink: "#1c2b1f"
  gate-muted: "#425244"
  gate-line: "#7e8a80"
  terrace-wash: "#e3efe5"
  madder: "#8e2f2b"
  terrace-leaf: "#3f5c38"
  rice-olive: "#53542f"
  gate-stone: "#6b6256"
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
    backgroundColor: "{colors.temple-green}"
    textColor: "{colors.chalk}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: "12px 18px"
  button-primary-hover:
    backgroundColor: "{colors.temple-green-hover}"
    textColor: "{colors.chalk}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: "12px 18px"
  button-rust:
    backgroundColor: "{colors.embroidery-rust}"
    textColor: "{colors.chalk}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: "12px 18px"
  button-rust-hover:
    backgroundColor: "{colors.embroidery-rust-hover}"
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
    textColor: "{colors.temple-green}"
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
    textColor: "{colors.temple-green}"
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
    textColor: "{colors.temple-green}"
    padding: "0px"
---

# Design System: Mike Bali AI

## 1. Overview

**Creative North Star: "The Guide at the Gate"**

Mike is still the guide at the gate, already talking. The interface should feel like that meeting in daylight, not at sunset and not in a brochure. Close, specific, in shade. Density is a working cabinet, not a campaign page. Type does the hospitality. Color is the shirt's stitch: temple green for the word, rust once, and a green-gray page.

The ground is shade, not the shirt. A tourist reads this on a phone. An admin reads it at a desk. Both need a light field with real contrast. The page is green-gray. It is never linen, cream, or sand.

This system rejects the generic slate SaaS dashboard (Segoe UI, gray panels), the luxury Bali resort brochure (gold serif, infinity pool, barefoot-luxury copy), the travel-blog cream and sand template, the neon beach-club / nightlife promo, and the corporate real-estate CRM.

**Key Characteristics:**

- One voice for the Telegram chat, the admin, and the partner cabinet
- Green-gray paper; the linen shirt stays in the portrait and never becomes a background
- Temple green does ordinary work; embroidery rust appears once; no gold fills
- Flat surfaces, a 1px stone line, a shadow only under a dialog
- Fraunces for the stitched name and page titles; Golos Text for everything said
- Short Russian labels that say what will happen

## 2. Colors

The palette is the shirt's stitch, corrected for WCAG 2.2 AA. Temple green is the wordmark. Embroidery rust is the single highlight. The page is green-gray shade. It is not the linen shirt, and it is not sand.

### Primary

- **Temple Green** (#2c4030): primary buttons, the wordmark, active navigation, and focus rings. White label text on this green is about 10.4:1.
- **Temple Green Hover** (#3e5342): the same green lifted one step, for hover and pressed primary buttons. White text stays above 7:1.

### Secondary

- **Embroidery Rust** (#8a4520): the single highlight in a view. The lead count, or the action that contacts a person or opens a place. About 6.3:1 as text on the page. White text on this rust is about 7:1.
- **Embroidery Rust Hover** (#6e3416): the same rust pressed darker.
- **Embroidery Thread** (#b46432): the portrait thread. It fails contrast for text and for white-on-fill. Not a UI color. Terrace Leaf (#3f5c38) is the chart slice in this family.

### Tertiary

- **Thread Gold** (#a07846): a chart slice only. Never a button fill, never a headline, never a background.

### Neutral

- **Warung Paper** (#f3f8f4): the page. A green-gray white, hue near 152, chroma under 0.01. Body backgrounds, the nav rail, the login field. Not cream, not sand, not the shirt.
- **Surface** (#fcfefc): panels, inputs, dialogs, and secondary buttons. One step lighter than the page, so a list sits on the paper without a drop shadow.
- **Chalk** (#ffffff): text on temple green, embroidery rust, and madder.
- **Terrace Ink** (#1c2b1f): body text and headings in the sans. About 14:1 on warung paper.
- **Gate Muted** (#425244): secondary text, placeholders, and unselected nav. About 7.5:1 on warung paper. This is the quiet voice.
- **Gate Line** (#7e8a80): 1px borders on panels, inputs, tables, and the nav rail. About 3.5:1 on warung paper, so the edge is visible.
- **Terrace Wash** (#e3efe5): the active nav row, the selected chip, and the hover of a secondary button.
- **Linen Shirt** (#e7cfb5): the portrait cloth. Reference only. See the rule below.
- **Madder** (#8e2f2b): errors. White text on madder is about 7.4:1. The wash behind an error is #f6e4e1, a small field only, never the page.
- **Terrace Leaf** (#3f5c38), **Rice Olive** (#53542f), **Gate Stone** (#6b6256): chart series, with temple green and embroidery rust. A chart still needs a text legend.

### Named Rules

**The Not-the-Shirt Rule.** Linen Shirt (#e7cfb5) is the portrait. It is never a page, panel, input, or button fill. Sand, cream, and beige are the same mistake. If a screen looks like a travel-blog template, the background is wrong. The page stays Warung Paper.

**The One Rust Rule.** Embroidery rust appears once per view, on the lead count or the action that contacts a person or opens a place. Enter, save, and navigate are temple green. Two filled buttons in one row are prohibited.

**The No Gold Rule.** No gold type, no gold buttons, no gold rules, no gold page. Thread gold is a chart slice with a text legend, or it is absent.

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

- **Dialog** (`box-shadow: 0 12px 32px rgb(28 43 31 / 0.14)`): modal forms and menus only. The tint is terrace ink, so the lift stays green-brown rather than neutral gray.
- **Focus** (`outline: 2px solid #2c4030; outline-offset: 2px`): every interactive control. The ring is temple green on the page, visible without a glow.

### Named Rules

**The Flat Gate Rule.** Surfaces are flat. Depth is a 1px gate line (#7e8a80). A shadow appears only under a dialog or a menu. If the shadow looks like a 2014 app, it is too dark and too tight: lighten it toward terrace ink at 14% and keep the blur at 32px.

## 5. Components

Controls are compact enough for a cabinet and large enough for a phone outdoors. Corners are lightly cut (8px on controls, 12px on panels, 4px on chips). Pills, full-bleed gradients, and side stripes are out.

### Buttons

Plain and pressed, like a shirt that has been worn in. One filled action per view.

- **Shape:** lightly cut corners (8px).
- **Primary:** Temple green fill, chalk text, label type, padding 12px 18px. Hover shifts to Temple Green Hover. Use for enter, save, and other ordinary commits.
- **Rust:** Embroidery rust fill, chalk text, same padding. The one action that contacts a person or opens a place. Hover shifts to Embroidery Rust Hover. Do not place it beside a primary button.
- **Secondary:** Surface fill, terrace ink text, 1px gate line, padding 8px 12px. Hover fills with terrace wash. Use for "Выйти" and for cancel.
- **Focus:** 2px temple green outline, 2px offset.
- **Disabled:** terrace wash fill, gate muted text, gate line border. No opacity fade. The label still clears 4.5:1.

### Chips

Partner types and filters. A chip is a choice, not a decoration.

- **Style:** surface fill, terrace ink text, 1px gate line, 4px radius, padding 4px 8px, label type.
- **Selected:** terrace wash fill, temple green text, 1px temple green border.
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
- **Placeholder:** gate muted (#425244). Same contrast bar as body text.
- **Focus:** border becomes 1px temple green, plus the 2px focus outline. No glow.
- **Error:** 1px madder border, and a madder message under the field in body type. The message says what to fix. The border is not the only signal.
- **Disabled:** terrace wash fill, gate muted text.

### Navigation

A left rail, 208px, warung paper, 1px gate line on the right. The wordmark sits at the top of the rail. Links are label type, sentence case, gate muted, with 8px 12px padding and 8px radius. Hover uses terrace wash. The active link is terrace wash with temple green text.

Below 960px the rail becomes a horizontal bar under the wordmark. Links wrap. The active link stays temple green on wash, so the section is obvious without a hamburger mystery.

The header on the cabinet only holds the secondary "Выйти" button, aligned to the end. It does not repeat the page title.

### Charts

Stats are a donut plus a legend, never a naked rainbow. Series order is fixed: Temple Green, Embroidery Rust, Rice Olive, Terrace Leaf, Thread Gold. "Other" uses Gate Stone.

- **Shape:** the ring is a stroke, not a gradient. Slice gaps are 1px of surface.
- **Legend:** every slice has a text label and a number beside a 10px swatch. The swatch is `aria-hidden`. Color is never the only label.
- **Empty:** one sentence in body type, gate muted: "Пока нет данных". No illustration.

### Wordmark

The signature. A two-prong candi, then the lockup, in temple green.

- **Mark:** two split gate prongs, 28px wide, current color. It appears once, at the top of the nav or on the login screen. It is not a repeating pattern, a background, or a bullet.
- **Name:** MIKE in Fraunces, about 1.25rem, weight 560, tracking -0.02em.
- **Role:** BALI GUIDE in Golos Text, 0.75rem, weight 600, tracking 0.08em, under the name. This is the logo, not a section eyebrow.

## 6. Do's and Don'ts

### Do:

- **Do** set the page to Warung Paper (#f3f8f4) and body text to Terrace Ink (#1c2b1f). Never linen, cream, or sand.
- **Do** use Temple Green (#2c4030) for the wordmark, primary buttons, active nav, and the focus ring.
- **Do** spend Embroidery Rust (#8a4520) once per view, on the lead count or the action that contacts a person or opens a place.
- **Do** keep panels flat, with a 1px Gate Line (#7e8a80) and 24px padding.
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
- **Don't** put two filled buttons in one row, or use Embroidery Thread (#b46432) or Thread Gold (#a07846) for text or fills.
- **Don't** carry meaning by color alone. Errors need a sentence. Charts need a legend. Selected chips need a state.
- **Don't** animate layout, bounce, or reveal content by hiding it until a class is added.
