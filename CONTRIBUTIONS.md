# Changes on top of upstream `esphome-p4-86-panel-eth-2ro-lvgl`

**Base version:** forked from upstream tag **`2026.07.02`**, then merged forward onto
upstream `main` @ `a090b2e` (2026-07-31) on 2026-08-15 — this branch tracks the latest
upstream revisions plus the features below.
**Upstream:** https://github.com/chrisdunnname/esphome-p4-86-panel-eth-2ro-lvgl
**This branch's file:** `esp32-p4-86-panel.yaml` (same filename as upstream — this is a
personal fork branch, not a PR submission; see "Status" below).

This document summarises every change made on top of the stock firmware, where each
change lives, and whether it is generally re-usable by other users. It follows this
repo's own `CONTRIBUTING.md` guidance: features are commented in-file (search for
`[FORK]`) and described here so they can, where practical, be isolated / included /
excluded by others.

**Status:** this is a personal fork, published for visibility/reference — not a pull
request. No PR has been opened against upstream. Feel free to cherry-pick anything
useful; the feature table below is meant to make that easy without having to read the
whole diff.

---

## 1. Feature summary

| # | Feature | New IDs / substitutions | Re-usable? |
|---|---------|-------------------------|------------|
| 1 | **Voice-assistant wake-sound latency fix + assist-button music pause/resume** | `assist_button_pressed` script, `music_paused_by_assist` global, reworked `voice_assistant` `on_end`/`on_idle`/`on_play` handlers | ✅ Yes — broadly useful |
| 2 | **Full-screen album art with smaller-resolution images** | `album_art_resize` substitution (256x256), `online_image`/`image` resize + LVGL `zoom`/`antialias` on `img_album_art` / `img_mc_art` | ✅ Yes |
| 3 | **Media picker + second media page** | `media_control_page`, scripts `apply_media_target` / `refresh_np`, `sp1..8` sensors, `media_target1..8` subs | ✅ Yes — substitution-driven, genericised on this branch |
| 4 | **`music_default_playlist` substitution** | `music_default_playlist` | ✅ Yes |
| 5 | **Generic climate slots (HVAC *or* temperature sensor per slot)** | `climate_hvac_count` substitution; reworked `climateN_item` handlers + tiles | ✅ Yes — slot 1 now uses upstream's own `climate_ac_page` rework (merged 2026-08-15); slots 2/3 still run the original substitution-driven generic-slots design |
| 6 | **Climate mode dropdown + current/target temp read-back on open** | `on_load` blocks on `climate_ac_page` / `climate_studio_page2` / `_page3` | ✅ Yes (bug fix) — ported onto upstream's new `climate_ac_page` widget ids for slot 1 during the 2026-08-15 merge |
| 7 | **Per-light detail ("studio") pages for all 6 lights** | `light_studio_page` / `_page2..6` | ✅ Yes |
| 8 | **Light reset presets** | `light_reset_hue` / `_sat` / `_kelvin` / `_brightness` substitutions + per-light reset button | ✅ Yes |
| 9 | **Light colour swatches (all 6 lights)** | 12-swatch grid on `light_studio_page`/`_page2..6` (hs_color + color_temp_kelvin presets) replacing hue/sat sliders | ✅ Yes |
| 10 | **Home Screen 2 (extra 6 launcher tiles)** | `home7..12_*` substitutions, `home_page_2_title`, `home_screen_2_hide_from_navigation` | ✅ Yes |
| 11 | **Spinbox / rotary-knob cursor & reset-knob UI tweaks** | small edits to spinbox / encoder handlers | ✅ Yes (minor polish) |
| 12 | **Tap listening/thinking/replying display to cancel voice assistant** | `on_click` on the 3 VA-state pages' root `obj`, guarded by `voice_assistant.is_running`, calls `voice_assistant.stop` (same action as the existing "stop" wake word) | ✅ Yes |
| 13 | **Bigger bottom nav bar + rebalanced page layout** | `top_layer` buttonmatrix height 50→75; all 17 content-grid pages switched `align: CENTER` → `TOP_MID` + `y: ${taskbar_height}`; `page_content_height` 600→575 | ✅ Yes — see in-file comments for the "why `TOP_MID`, not `CENTER`" reasoning if you resize the nav bar again |
| 14 | **ETH-2RO relay control** | `relay1_pin`/`relay2_pin` substitutions (GPIO32/GPIO46 per Waveshare's wiki), two `switch: platform: gpio` entities, repurposed `controls_page` slots 2/3 for on-panel toggle buttons | ✅ Yes — only relevant if your board has the ETH-2RO expansion fitted |

Not included on this branch: a bespoke "car page" (BYD Shark EV charging control) present
in the maintainer's live personal config — dropped here as it's not generally reusable
and references a specific vehicle integration.

---

## 2. Detail & rationale

### 1. Voice-assistant latency + music pause/resume
Root cause of the 2–4 s wake-sound lag: the ES7210 mic (16 kHz) and ES8311 speaker
(48 kHz) share one I2S clock bus, so they **cannot run simultaneously**. The stock
wake-beep contended with the mic. Handlers were reworked so the beep no longer blocks
listening. Added `assist_button_pressed`: if the panel is playing its own audio when
the assist button is pressed, it pauses that playback (`music_paused_by_assist` global)
and auto-resumes when the assistant goes idle.

### 2. Full-screen album art, smaller images
`album_art_resize` fetches art at 256×256 (lower bandwidth / loop cost) and LVGL scales
it up with `zoom` + `antialias`, restoring the full-screen look without large downloads.

### 3. Media picker + second media page (`media_control_page`)
Lets the user pick which media target the panel controls and shows now-playing on a
second page. Substitution-driven (`media_target1..8_name`/`_entity`) so any user can
plug in their own list of players. **Note:** this adds a number of Home Assistant
`text_sensor`s and a `refresh_np` album-art refresh; on a busy device it contributes to
main-loop load.

### 5–6. Generic climate slots + read-back on open
`climate_hvac_count` (default `3`) sets how many climate slots are HVAC units
(`climate.*`); the remaining slots become read-only temperature sensors (`sensor.*`).
Slot 1 was independently reworked by the upstream author (2026-07-31, commit
`9a8b6fc`) into a nicer native-spinbox UI (`climate_ac_page`); that rework was missing
two bug fixes from this branch (stale mode-dropdown / stale current-temp on page open),
which were ported onto the new widget ids during the 2026-08-15 merge. Slots 2/3 are
untouched by upstream and still run the original substitution-driven generic-slots
design.

### 9. Light colour swatches
Replaces the clunky hue/sat sliders with a tappable 12-swatch grid (6 saturated colours,
purple/pink/magenta, and 3 white colour-temperatures), applied to all six light detail
pages. Each light's `lightN_hscolor` sensor's slider-sync `on_value` is neutralised (the
sliders no longer exist).

### 12. Tap-to-cancel voice assistant
Lets you interrupt the assistant by tapping its own display instead of only via the
"stop" wake word or holding the mic button again. Reuses the exact `voice_assistant.stop`
action the existing "stop" wake-word model calls, so cleanup (phase reset, navigation
back to the default page) goes through the same already-working path.

### 13. Bigger nav bar
The `align: CENTER` layout only worked because the original header/content/footer split
(50/600/50) happened to be symmetric — centering can't asymmetrically grow just the
bottom bar's clearance without wasting equal growth at the top. Switched every
content-grid page to `align: TOP_MID` + explicit `y` offset so future nav-bar resizes
only need a relative height adjustment, not a layout rewrite.

### 14. ETH-2RO relay control
Per Waveshare's wiki (§5.6.3 Relay Control), the expansion board's two relays are on
GPIO32 and GPIO46 — plain GPIO output, opto-isolated on the board itself. Exposed as two
`switch` entities (register with Home Assistant automatically) and wired into the
existing generic `controls_page` framework (slots 2/3, which were unused upstream
placeholders) for on-panel toggle buttons — no new LVGL widgets needed.
