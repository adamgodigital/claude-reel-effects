---
name: effects
description: Edit talking-head videos with 55 effects, word-by-word captions, sound effects and automatic pause trimming (orbit, spotlight, pop-word, logo-link with real brand logos, card-drop, halftone-paper, glass widgets, checklist, comment box, iMessage pop-ups, place-in-grid and more). Effects track the speaker's face and can sit behind their head. Use when the user types /effects, names one of the effects, or asks to add captions, an effect, zoom, grade, sticker, animation or sound effects to a video, cut the pauses, or edit a talking-head video.
---

# Effects: 55 video effects, captions, sound and pause trimming (Adam Digital edition)

The user is usually not technical. Keep replies short and friendly, do the work for them, and never ask them to run commands themselves.

All paths below are relative to this skill's folder (the folder this SKILL.md is in). Use its absolute path in commands. On Windows, the Python is at `.venv\Scripts\python.exe` instead of `.venv/bin/python`.

## 1. First run: set up (once)
Run `bash scripts/setup.sh`. It prints `READY` when done (the first time takes 1 to 3 minutes).
- `NEED_FFMPEG`: install it for them. On a Mac: `brew install ffmpeg` (if `brew` is missing, tell them to install Homebrew from brew.sh first). On Windows: `winget install ffmpeg`.
- `NEED_PYTHON`: install Python 3.12 (Mac: `brew install python@3.12`, Windows: `winget install Python.Python.3.12`), then run setup again.
- Then run `.venv/bin/python scripts/fx.py --profile`. If it says `not set yet`, ask once for their name and Instagram handle and save them: `.venv/bin/python scripts/fx.py --profile "Their Name" "@theirhandle"`. Effects with a profile card show these.

## 2. Work out what they want
- Video: the user drags the file into the chat, or gives a path. A vertical phone video works best.
- One effect: `/effects orbit from 3 to 6 seconds` → just that effect.
- Captions: "add captions" or `/effects captions` → the `captions` effect over the whole clip, style `clean` unless they pick `bold`, `pill` or `grey`.
- Cut the pauses: "cut the pauses", "jump cuts", "remove the silences" → step 3.
- Full edit: "edit this", "make it a reel", `/effects full edit` → the full edit recipe below.
- Match their words to the tables below. Unsure? Show them the list.

## 3. Cut the pauses (only when asked, or in a full edit)
`.venv/bin/python scripts/trim.py <video> <video-name>_trim.mp4`, then work on the trimmed file. It keeps a short breath between lines and keeps their normal pace (`--speed 1.1` only if they ask for faster). Tell them how much time it saved.
Do this before planning anything else: if they gave timings in seconds for the original video, don't trim unless they ask, because every time after a cut moves.

## 4. Find the words (timing and captions)
`.venv/bin/python scripts/words.py <video>` prints each word with its time and saves `<video>.words.json`.
- Use it for "on the word X" or "when I say ...".
- `captions` and `halftone-paper` need it (fx.py runs it by itself if the file is missing).
- Read the transcript. Fix misheard names and numbers in the `.words.json` before rendering ("clot code" → "Claude Code", "24 -7" → "24/7"), keeping one entry per word.
- Short windows look best: 1.5 to 4 seconds per effect.

## 5. Draft, check, render
1. Write the plan next to their video as `<video-name>_effects.json`:
   ```json
   {"effects": [
     {"fx": "logo-link", "start": 0.0, "end": 2.0, "text": "anthropic|claude"},
     {"fx": "pop-word", "start": 4.6, "end": 5.7, "text": "24/7"},
     {"fx": "captions", "style": "clean", "keywords": "claude|duet|24/7"}
   ]}
   ```
   `captions` needs no start and end: it runs over the whole clip.
2. Check frames first (fast): `.venv/bin/python scripts/fx.py --plan <plan.json> <video> <folder>/check.png --still 1.2,5.0`, using the middle of each effect. Look at the PNGs yourself. Fix the text, timing or options if something looks off (covers the face, cut off by the edge, unreadable, two things fighting for the same spot).
3. Render: `.venv/bin/python scripts/fx.py --plan <plan.json> <video> <video-name>_effects.mp4`. It keeps their voice and adds quiet sound effects as effects land (`--no-sfx` for none, `--sfx-volume -4` for quieter, or `"sfx": false` in the plan). It renders at 1080p; add `--width 2160` for 4K (slower).
4. Tell them where the file is. Remind them in one line to watch it before posting: it drafts, they approve.

A single effect needs no plan: `.venv/bin/python scripts/fx.py orbit <video> <out.mp4> --start 3 --end 6 --text "..." --opt key=value`.

## Full edit recipe (the Adam Digital way)
1. Cut the pauses (step 3). Get the words (step 4) and fix names.
2. Captions on, style `clean`: white words, one keyword per short phrase in gold serif italic. Pass `keywords` with the product names, numbers and the verbs being shown.
3. One effect every 3 to 6 seconds, 1.5 to 4 seconds each, landing on the spoken word:
   - Hook (first 2 seconds): `logo-link` when two brands or products are named, otherwise `pop-word` on the brand or the big claim.
   - "What it does" lines: `card-drop` with a screenshot they give you. Lists: `checklist` or `todo`. Numbers: `liquid-glass-graph` or `select-resize`. Comparisons: `swipe` or `tier-list`.
   - Punchlines: `pop-word` (yellow), `reject-stamp` on "no" or "not", `lean-in` on emphasis.
   - One breather: `halftone-paper` for a 4 to 6 second explanation.
   - Call to action: `comment-box` with their keyword, or `tap` on "follow".
4. Never stack two big things at once. Captions step aside on their own while a lower-screen card is showing.
5. Keep the sound effects on: quiet pops and ticks, no whoosh on every cut.

## The 51 effects
| # | `fx` name | What it does | Options (all optional) |
|---|---|---|---|
| 1 | `noise` | Reels pile up behind your head, one every quarter second | `images` (folder of screenshots or clips), `size` |
| 2 | `lineup` | Numbered tiles fan out in an arc above your head | `text` (tile names joined with `\|`) |
| 3 | `locked-on` | Corner brackets snap onto your face, the camera follows you | `zoom` (default 1.35), `text` (tag) |
| 4 | `orbit` | Your reels circle your head: in front at the bottom, behind at the top | `images`, `count`, `speed`, `size` |
| 5 | `lean-in` | A fast punch-in on one word | `zoom` (default 1.45, max 2), `speed` |
| 6 | `backdrop-word` | A giant word drops in behind you | `text`, `color` (hex), `font` (`bold` or `serif`) |
| 7 | `spotlight` | Kills the lights, keeps you lit | `text` (glowing word behind you), `color`, `push` |
| 8 | `the-bill` | Prints your instructions like a receipt into the wall above your head | `text` (lines joined with `\|`) |
| 9 | `moody` | A moody colour grade | `grade` (`moody`, `bw`, `warm`, `cool`, `pop`) |
| 10 | `swipe` | A before and after slider sweeps across you | `grade` (the "after" look) |
| 11 | `todo` | A checklist card beside your head ticks off as you talk | `text` (items with `\|`), `ticks` (video seconds with `\|`), `title` |
| 12 | `comment-box` | An Instagram comment bar types a word and posts it | `text` (default EFFECTS) |
| 13 | `tap` | A Follow button pops up and flips to Following | `at` (video second of the flip), `x`, `y` (0 to 1), `color` |
| 14 | `pause-point` | Freezes the frame and points at you with a hand-drawn arrow | `text` (label), `color`, `label_x` |
| 15 | `uninstall` | A glitchy uninstall bar breaks the frame apart | `text` |
| 16 | `reel-frame` | Your video shrinks into an Instagram reel card | `text` (handle) |
| 17 | `shortcut-rain` | Keyboard keys rain down behind you | `text` (keys with `\|`), `count` |
| 18 | `reject-stamp` | A big red stamp slams onto the screen | `text`, `color`, `angle`, `y` |
| 19 | `countdown-flip` | A 3, 2, 1 flip clock above your head | `from` |
| 20 | `rabbit-hole` | The frame tunnels into itself, spinning | `ratio`, `speed`, `spin` |
| 21 | `cover-star` | You become a magazine cover, title behind your head | `text` (title), `lines` (with `\|`), `issue`, `color` |
| 22 | `scribble` | Marker doodles draw themselves around you | `text` (label), `color` |
| 23 | `glass-widgets` | Frosted glass widgets and mini artifacts float around your head, plus an Edited by Claude pill | `text` (big number), `name`, `handle`, `look` (`simple` for the 3-widget version) |
| 24 | `red-collage` | Black and white you, a giant red word behind, three lines slam in | `text` (red word), `lines` (with `\|`), `tag` |
| 25 | `split-headline` | A headline card slides down and pushes you to the bottom half | `text` (lines with `\|`), `hl` (highlighted word), `pill` |
| 26 | `pastel-word` | Lavender room, giant word behind you, a profile card gets followed | `text`, `name`, `handle` |
| 27 | `check-pills` | Grid-paper room, reel boards behind you, a cursor clicks blue pills | `text` (pills with `\|`), `images` |
| 28 | `timeline` | A dark red film grade with an editing timeline, a REC timecode and a glowing playhead | `text` (title), `sub`, `tc` |
| 29 | `headline-box` | A punch-in with a two-line headline, the second line in a white box | `text` (lines with `\|`), `zoom` |
| 30 | `profile-wall` | Your reels grid fills the wall behind you while a counter ticks up | `images`, `count`, `label` |
| 31 | `tier-list` | A tier list drops in and Claude flies into S tier | `title`, `item`, `others` |
| 32 | `broll-split` | B-roll on top with a price-tag sticker, you below | `images`, `text` (tag) |
| 33 | `phone-fan` | Your reels fan out like a hand of phones under a headline | `images`, `text` (lines with `\|`) |
| 34 | `dot-reveal` | Your shot builds out of glowing dots, then snaps to the full picture | `color`, `cell` |
| 35 | `headline-wall` | Your own headlines pile up behind your head, then a total pops in front | `text` (`headline::meta\|...`), `total`, `label` |
| 36 | `checklist` | A Claude task list under your chin: each step spins, then ticks green | `text` (`step::meta\|...`), `title` |
| 37 | `liquid-glass-graph` | A liquid glass card under your chin: a green graph climbs while the number counts up | `text` (label), `from`, `to` (e.g. `197K`, `59%`), `color` |
| 38 | `carousel-spin` | Your reels spin around you in a 3D carousel, then slow to a stop | `images`, `count`, `size`, `turns` |
| 39 | `match-cut` | News pages cut on one word, locked in a red box behind your head | `text` (the word, default Claude), `color` |
| 40 | `apple-toggles` | An iPhone settings card under your chin flips its switches on, one line at a time | `text` (rows with `\|`), `ticks` (seconds with `\|`), `color` |
| 41 | `led-sign` | The lights drop and a glowing LED sign types itself out behind you | `text` (lines with `\|`), `color`, `push` |
| 42 | `slow-push` | A slow cinematic push-in to your face while the room melts out of focus | `zoom` (default 1.6), `blur` |
| 43 | `over-the-shoulder-zoom` | The camera pushes into one top corner and a see-through liquid glass graph pops beside your head (line climbs, number counts up), pulls back, then the other corner with a second, related bar graph. Your head stays in front | `text` (two labels with `\|`), `to` (two numbers with `\|`, e.g. `197K\|672K`), `zoom` (default 2.0) |
| 44 | `messages` | iMessage notifications pop in one after another, creamy glass with a soft glow, stacking up above the bottom of the frame | `text` (messages with `\|`), `title` (default Messages), `y` |
| 45 | `place-in-grid` | You shrink into the centre tile of your 3x3 profile grid on frosted glass, then 8 reels pop in around you, one per frame, with Instagram view counts on every tile | `images` (folder of your reels or covers), `views` (9 counts with `\|`, the 9th is yours) |
| 46 | `tape-label` | A level strip of yellow tape with your line lands on your chest, kept off your face | `text` |
| 47 | `select-resize` | A blue selection box with handles grabs your number above your head and a cursor drags it bigger | `text` (default 2X) |
| 48 | `wave-trim` | A dark panel above your head shows your voice; the red dotted silence on both ends collapses until only your words are left (a visual only: to really cut pauses, use step 3) | none |
| 49 | `huge-strike` | One huge serif word wipes in behind your head, then a red line crosses it out | `text`, `at` (seconds into the effect when the strike lands, default 0.6) |
| 50 | `crayon-write` | A red crayon writes your word behind your head, then underlines it and flies off | `text` |
| 51 | `fan-build` | Your reel covers deal into a fan behind your head, one card at a time | `images` (folder of your covers), `count` (default 13) |

**Named looks** (same effect, a fancier look; they don't add to the count):
- `glitter-spotlight` = `spotlight` with `look=sparkle`: the room goes dark, golden rays burst from behind your head, a big gold word with a shine sweep, twinkling sparkles and a glow around you. `text` (the word), `color`, `push`.
- `cover-star` with `look=editorial`: a soft warm film look, a classic serif masthead behind your head, an issue line and elegant cover lines. `text` (masthead), `issue`, `lines` (3 lines with `\|`), `right` (lines with `\|`), `color`, `accent`, `lines_y`, `right_y`.
- `liquid-glass-graph` with `look=bento`: the climbing graph moves to a smoked glass screen behind your head, with glass bento tiles in front of you (a donut, a KPI, bars). `text`, `from`, `to`, `donut` (`29%::label`), `kpi` (`672K::label`), `bars` (`197\|140\|124::label`).
- `apple-toggles` now sits above you, tucked behind your head, with a gentle zoom (`pos=below` for the old under-the-chin card; `overlap`, `zoom`).

Aliases work too: `bill`, `to-do`, `follow`, `stamp`, `countdown`, `cover`, `rain`, `pause`, `wave`.

## Adam Digital effects and captions
| # | `fx` name | What it does | Options (all optional) |
|---|---|---|---|
| 52 | `pop-word` | A huge bold word pops in behind your head; the top of your head covers the bottom of it | `text`, `color` (hex), `brand` (use a brand's colour, e.g. `claude`), `size` (`big`) |
| 53 | `logo-link` | Two real brand logos pop in beside your face, joined by a dashed line that runs behind your head | `text` (two brands with `\|`, e.g. `anthropic\|claude`), `label` (names under the tiles, with `\|`), `logo` (your own logo files with `\|`) |
| 54 | `card-drop` | You slide down and a floating card with a screenshot pops in above you; captions move under the card | `image` (path to a screenshot), `fit` (`cover` to fill the card), `text` (shown if there's no image) |
| 55 | `halftone-paper` | A cream paper page: you cut out bottom-right with a halftone shadow, your spoken words building at the top with red serif keywords | `keywords` (with `\|`), `text` (your own headline instead of your words), `scale`, `x` |
| + | `captions` | Word-by-word captions. `clean`: white words, keywords in gold serif italic. `bold`: one big word at a time, yellow keywords. `pill`: short phrases on a dark pill. `grey`: small grey-pill subtitles | `style`, `keywords` (with `\|`; otherwise names and numbers are picked for you), `hide` (`3.5-6\|20-22`), `y` (0 to 1) |

Aliases for these: `pop`, `big-word`, `logo`, `logos`, `link`, `card`, `drop`, `paper`, `halftone`, `caption`, `subtitles`, `subs`.

Real logos: `logo-link` draws 109 bundled brand logos (Claude, Anthropic, Gemini, Perplexity, Meta, GitHub, Notion, Figma, WhatsApp, Instagram, TikTok, YouTube, X, Gmail, Zapier, n8n, Cursor, ElevenLabs, Hugging Face, Mistral, DeepSeek and more; run `.venv/bin/python scripts/logos.py` for the full list). Some brands aren't bundled (OpenAI, Microsoft, LinkedIn, Slack, Canva and others): ask the user for the official logo file, or download it from the brand's own press or brand page, and pass it as `logo=path.png`. Never draw a logo by hand.

## Rules
- Never cover the face. Everything either goes behind the person or avoids the face by itself; if a check frame still shows text over the face, move it (`x`, `y`) or shorten the text.
- Effects run in the order listed. Put camera effects (`locked-on`, `lean-in`, `spotlight`, `card-drop`) first when they overlap others. Captions are always drawn last, on top.
- Zoom never goes past 2x, so the video stays sharp.
- Charts, counters and headlines use the user's real numbers. Ask if you don't know them.
- Sound effects are made in code (no sample files). Background music isn't added: suggest CapCut for that.
- These are drafts. If the user compares them to a reel they saw, be honest that hand-tuned timing and sound design can go further.
