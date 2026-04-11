# Theory in Practice — Redesign Plan & Master AI Prompt

**For:** Jonathan (building for Roti Akinsanmi)
**Goal:** Ship a visionary, monochromatic, interaction-rich redesign — fast. No multi-week plans.
**Benchmarks:** aixor-react.vercel.app, oddcommon.com, decoupling.co

---

## 0. One thing missing before we start

You said *"Here is a ton of feedback he has received"* — but no feedback document was actually attached to the message. I can only see the three generic testimonials already in `theory_in_practice_copy.md`.

**Action for you:** drop the raw feedback into a new file at `theoryinpractice/feedback_raw.md` (paste emails, LinkedIn comments, course evals, Mount Royal reviews, Slack screenshots — anything). Once it's there, I will:

1. Log every quote with attribution and year
2. Categorize by theme: *Clarity of thinking · Frameworks that stuck · Monday-morning change · Teaching craft · Leadership presence · Humour/personal*
3. Surface the 5–8 that most viscerally show **"theory in practice"** — the ones where someone says "I used it the next morning" or "it changed how we plan"
4. Write them into the new site under a dedicated *Voices* section

Until then, the current 3 quotes are placeholders.

---

## 1. The simplest possible stack (ship this weekend)

Everything stays on Cloudflare. No separate backend, no Supabase, no Next.js, no build step you have to babysit.

| Layer | Tool | Why |
|---|---|---|
| Hosting | **Cloudflare Pages** (already set up) | Git push → live in 30s |
| Site | **Single `index.html`** + one JS file + one CSS file | No framework. No build. Editable in any text editor. |
| Login (Roti only) | **Cloudflare Pages Function** + **Resend** | 4-digit PIN emailed to `roti@akinsamni.com`, session cookie signed with a secret |
| Editable content | **Cloudflare KV** (free tier: 100k reads/day) | Text lives as JSON in KV; the page fetches it on load; Roti edits inline when logged in, hits save, PUT to KV |
| Contact form | **Cloudflare Pages Function** → **Resend** → `roti@akinsamni.com` | Roti's email never on the page; Resend keeps the audit log |
| Email sender | **Resend** with a verified sender on `theoryinpractice.ca` | Single API key for both flows |

**Total moving parts:** 1 HTML file, 1 CSS file, 1 JS file, 3 Pages Functions (`/api/login`, `/api/verify`, `/api/content`, `/api/contact`), 1 KV namespace, 1 Resend account, 1 environment-variable secret.

That's it. No database. No user table (there is exactly one user). No CMS.

### Auth flow in plain English
1. Roti hits `?login` → page shows an email field pre-filled with `roti@akinsamni.com` → clicks *Send code*
2. `POST /api/login` → Pages Function generates a random 4-digit PIN, stores `{pin, expiresAt}` in KV under key `auth:pending`, sends the PIN via Resend. Nothing else on the planet can request this because the endpoint hard-codes the allowed email to `roti@akinsamni.com`.
3. Roti types the PIN → `POST /api/verify` → if it matches and hasn't expired, Function sets a signed, httpOnly cookie (`tip_session`, 30 days) and returns `{ok:true}`
4. When the cookie is present, the frontend shows *Edit* buttons next to every editable text block. Click → contentEditable → blur → `PUT /api/content` writes the new JSON blob to KV. Function checks the cookie signature before accepting the write.

### Content model
Single JSON blob in KV at key `content:v1`:
```json
{
  "hero": { "theory": "...", "practice": "...", "overlap": "..." },
  "academy": { "intro": "...", "modules": [ {...} ] },
  "consulting": { "intro": "...", "steps": [ {...} ] },
  "about": { "bio": "...", "credentials": [...] },
  "partners": { ... },
  "voices": [ { "quote": "...", "attr": "...", "year": 2025 } ]
}
```
Page loads → `GET /api/content` → hydrates the DOM. If the fetch fails, fall back to the defaults baked into the HTML so the site never breaks.

### What Roti can edit
Only text. No images, no layout, no colours. Every `<span data-edit="hero.theory">` becomes editable when logged in. Anything not tagged `data-edit` is locked. This keeps the UI pristine and means Roti literally cannot break anything.

### What it costs
$0/mo. Cloudflare Pages + Functions + KV free tier + Resend free tier (3,000 emails/month) covers everything a 1-person consulting site will ever need.

---

## 2. Design direction (the non-negotiables)

- **Monochromatic.** Near-black background (`#0A0A0A` or warm `#0B0A08`), bone/paper text (`#F5F1EA`), mid grey (`#7A756D`). One accent: **rust red `#B83A10`** used like punctuation — never as a block, never as a button fill except on hover. Think 2% of the pixels, not 20%.
- **Typography.** Serif display (Cormorant Garamond or PP Editorial New) for *Theory / Practice / Theory in Practice*. Mono for eyebrows, metadata, navigation (DM Mono / JetBrains Mono). Humanist sans for body (Inter Tight or Söhne).
- **No stock imagery. Ever.** No boardrooms, no whiteboards, no handshake photos, no laptops-on-desks. Imagery is either: (a) typographic, (b) the Venn diagram and its variants, (c) high-grain black-and-white close-ups of Roti (when you supply them), (d) abstract generative shapes that echo the Venn — overlapping circles, intersecting lines, field diagrams.
- **Kill the tiny useless icons.** The little widgets in your screenshot go. Replace with generous whitespace and quiet monospace labels (`— 01`, `— 02`).
- **Motion.** Lenis smooth scroll. Custom cursor that grows on hover (aixor-style). Section transitions on scroll via Intersection Observer — text reveals with a soft mask/clip-path wipe, not a bouncy fade. Venn diagram: circles drift into position on load, then respond subtly to cursor parallax. Nothing jumpy. Nothing slow.
- **Hero = the Venn diagram.** Two large circles, *Theory* and *Practice*, overlapping into *Theory in Practice*. SVG, animated draw-in on load (~1.2s), parallax-linked to cursor. The words breathe.
- **Navigation.** Fixed, minimal, left-side logo + right-side mono nav. Mega-menu on Academy/Consulting hover, aixor-style — full-width panel, dark, quiet.
- **No "book a call" button fight.** One CTA in the nav, one form at the bottom. That's it.

---

## 3. Site architecture (one page, anchor-scrolled)

1. **Hero** — Venn diagram, single line eyebrow, scroll cue
2. **Premise** — a quiet one-screen statement: *"Judgment to act differently on Monday."*
3. **Academy** — three tabs (Delivery Fundamentals · Human & Change · Risk & Governance), each with its module questions as the visual content. Questions first, answers implied.
4. **Proof strip** — `12 years · 1,500+ participants · 4/4 rating · ★ 2026 Teaching Excellence Award`
5. **Voices** — the feedback section I'll build once you paste the raw feedback. Large serif pull-quotes, mono attributions, one per viewport.
6. **Consulting** — the 4-step Discover / Design / Deliver / Debrief cycle as a visual loop (not four cards). One case study below: Global Engineering Firm.
7. **About — Roti** — serif bio, credentials as a tight mono list, portrait placeholder (you'll supply later).
8. **Partners** — Mount Royal University + Tarka Consulting, side by side.
9. **Contact** — single form: Name · Organisation · What are you working on. One submit button.
10. **Footer** — © 2026 Theory in Practice Inc. · Calgary · theoryinpractice.ca

---

## 4. The master AI design prompt

Copy-paste this into Kimi, Google Stitch, v0, Lovable, Claude artifacts, whatever. It's self-contained.

```
Design a single-page website for "Theory in Practice" — a product management
and product leadership academy + consulting practice run by Roti Akinsanmi, a
Mount Royal University instructor (2026 Teaching Excellence in Lifelong
Learning Award winner) with 12+ years teaching 1,500+ practitioners across
North America.

POSITIONING
Roti is a visionary product leader. The brand promise is one line:
"Applying models to real-world situations. Judgment to act differently on Monday."

AESTHETIC
Monochromatic and editorial. Near-black warm background (#0B0A08), paper
text (#F5F1EA), mid-grey (#7A756D). One accent colour only: a rust red
(#B83A10), used sparingly — as punctuation, never as a block fill. No more
than ~2% of the pixels should carry the accent.

Typography: serif display (Cormorant Garamond, PP Editorial New, or similar
high-contrast serif) for the words "Theory", "Practice", "Theory in Practice"
and all H1/H2. Monospace (DM Mono, JetBrains Mono) for eyebrows, section
numbers, metadata, nav. Humanist sans (Inter Tight, Söhne) for body.

Absolutely no stock photography. No boardrooms, whiteboards, laptops, or
handshake photos. Imagery is typographic, geometric, or editorial
black-and-white portraiture. Abstract overlapping circles and intersecting
lines echo the Venn concept.

REFERENCES (study these and match the sophistication level)
- aixor-react.vercel.app — cursor, hero energy, mega-nav
- oddcommon.com — restraint, typography, quiet confidence
- decoupling.co — monochrome editorial feel

HERO
A large animated Venn diagram is the hero. Two circles overlap:
- Left circle: "Theory" — a set of principles on which the practice of an activity is based.
- Right circle: "Practice" — repeated action.
- The overlap reads "Theory in Practice — applying models to real-world situations."
Serif display type. Circles draw in on load (~1.2s ease), then drift subtly
with cursor parallax. The only accent colour on the page appears inside
the overlap.

INTERACTION & MOTION
- Lenis (or equivalent) smooth scroll.
- Custom circular cursor that softly scales on interactive elements
  (aixor-style).
- On-scroll reveals using a clip-path / mask wipe — NOT fade-in-up. Quiet,
  confident, no bouncing.
- Sticky left-aligned section labels as the user scrolls a section.
- Fixed minimal top nav with mega-menu panels on Academy and Consulting hover.
- No parallax on body text. No marquee. No auto-playing video.

SECTIONS (in order)
1. Hero — Venn diagram + scroll cue
2. Premise — one-sentence statement filling a full screen
3. Academy — three tabs (Delivery Fundamentals / Human & Change Dynamics /
   Risk & Governance), each revealing 3–4 module cards. Each module is a
   QUESTION, not a feature (e.g. "What should we build, and why?").
4. Proof strip — 12 Years · 1,500+ Participants · 4/4 Consistent Rating ·
   ★ 2026 Teaching Excellence Award
5. Voices — large serif pull-quotes from past participants, one per viewport
6. Consulting — a 4-step cycle (Discover · Design · Deliver · Debrief)
   visualised as a LOOP, not 4 cards. The loop emphasises iteration.
   Below it, one case study: a Global Engineering Firm, Project Controls.
7. About — Roti's bio, credentials as a mono list, space for a
   black-and-white portrait.
8. Partners — Mount Royal University (Academy) and Tarka Consulting
   (Consulting delivery), side by side.
9. Contact — single form: Name · Organisation · What are you working on.
10. Footer — © 2026 Theory in Practice Inc. · Calgary, Alberta.

COPY IS FIXED — DO NOT REWRITE
Use the exact copy from the source document (hero, academy modules,
consulting steps, about, partners). Your job is layout, hierarchy, motion,
and type — not the words.

TECHNICAL CONSTRAINTS
- Single HTML file, one CSS file, one JS file. No build step.
- Vanilla JS or minimal libraries (Lenis is allowed).
- Hosted on Cloudflare Pages.
- Fonts loaded from Google Fonts or Fontshare.
- Must pass Lighthouse Performance ≥ 90 on mobile.
- Fully responsive: 360px → 1920px.

DELIVERABLE
One self-contained HTML file I can drop into a Cloudflare Pages repo.

What NOT to do
- No gradients beyond subtle noise/grain.
- No glass-morphism, no neumorphism, no drop shadows on cards.
- No icons from Lucide/Feather inside the content (mono labels only).
- No generic "trusted by" logo walls.
- No "Book a demo" SaaS energy. This is a practitioner's site, not a startup's.
```

---

## 5. LinkedIn banner strategy

Roti needs a LinkedIn header (1584 × 396) that visually matches the site. Three options, all ship-able in a day:

1. **The Venn, cropped.** A horizontal slice of the hero Venn diagram — the overlap sits left-of-centre, the words *Theory in Practice* in rust red inside it. Black background, paper-coloured serif type at the far right: *"Applying models to real-world situations."* Mono sub-line: *Roti Akinsanmi · Product Leadership · Calgary*.

2. **Editorial portrait.** High-contrast B&W close-up of Roti (you'll shoot or supply), bleeding off the left edge. Right side: rust red vertical rule + serif pull-quote *"Judgment to act differently on Monday."* Mono tag in the bottom-right: *theoryinpractice.ca*.

3. **Type only.** Full-width *Theory in Practice* in huge serif, set on the warm near-black. Under it, a hairline rule and a monospace line: *Product Management · Academy · Consulting · est. 2014*. Most versatile; works before any photography exists.

I'd ship **Option 3** first (can be generated today, no photography needed), then replace with Option 2 once Roti provides a portrait.

---

## 6. Ship order (half a day, not half a month)

1. **Paste the raw feedback** into `feedback_raw.md` — I'll categorize and select.
2. **Confirm the design prompt above** — you run it through Kimi and Stitch in parallel, pick the winner or merge two, and drop the HTML into the repo.
3. **I'll wire up the Cloudflare Functions** (`/api/login`, `/api/verify`, `/api/content`, `/api/contact`), the KV namespace, the Resend key, and the inline-edit JS. That's maybe 150 lines of code total.
4. **Roti logs in, tweaks a sentence, we publish.** Git push → live in 30 seconds per the CLAUDE.md rule.
5. **Banner:** generate Option 3 same day.

No weeks. Days.

---

## 7. Decisions I need from you before I write code

1. **Feedback file** — paste it so I can categorize (blocker for the Voices section).
2. **Resend sender domain** — is `theoryinpractice.ca` already set up in Resend with DNS verified? If not, that's a 10-minute DNS task on Cloudflare.
3. **Cloudflare account** — are you comfortable me adding a KV namespace and Pages Functions to the existing project, or do you want to click through it yourself and paste the binding name?
4. **Roti's email** — you wrote `roti@akinsamni.com` twice. Is that the correct spelling, or should it be `akinsanmi.com` (matches the LinkedIn URL in the copy doc: `linkedin.com/in/akinsanmi`)? This matters because the auth Function will hard-code it.
5. **Which design** — once Kimi and Stitch return their versions, do you want me to pick, or will you?
