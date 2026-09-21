# Changes on top of upstream `esphome-p4-86-panel-eth-2ro-lvgl`

**Base version:** forked from upstream tag **`2026.07.02`**, then merged forward onto
upstream `main` @ `a090b2e` (2026-07-31) on 2026-08-15 and `1c5132f` (`2026.09.17`) on
2026-09-21 — this branch tracks the latest upstream revisions plus the features below.
**Upstream:** https://github.com/chrisdunnname/esphome-p4-86-panel-eth-2ro-lvgl
**This branch's file:** `esp32-p4-86-panel.yaml` (same filename as upstream — this is a
personal fork branch, not a PR submission; see "Status" below).

This document summarises every change made on top of the stock firmware, where each
change lives, and whether it is generally re-usable by other users. It follows this
repo's own `CONTRIBUTING.md` guidance: features are commented in-file (search for
`[FORK]`) and described here so they can, where practical, be isolated / included /
excluded by others.

**Status:** this is a personal fork, published for visibility/reference. No PR has been
opened against upstream. The media player (#2–4 below) is also kept as a standalone,
upstream-ready branch, `media-player-upgrade`, containing only that change. Feel free to cherry-pick anything
useful; the feature table below is meant to make that easy without having to read the
whole diff.

---

## 1. Feature summary

| # | Feature | New IDs / substitutions |
|---|---------|-------------------------|
| 1 | **Voice-assistant wake-sound latency fix + assist-button music pause/resume** | `assist_button_pressed` script, `music_paused_by_assist` global, reworked `voice_assistant` `on_end`/`on_idle`/`on_play` handlers |
| 2–4 | **Media player: speaker picker, now-playing with album art, optional Music Assistant extras** (replaces the stock media page; same as branch `media-player-upgrade`) | `media_page` (rebuilt), `library_browse_page`, `media_set_page`; `media_target_count`, `media_target1..8_name`/`_entity`, `media_music_assistant`, `music_default_playlist`, `album_art_resize` substitutions; `apply_media_target` / `refresh_np` scripts; Home Assistant side in `home_assistant/` |
| 5 | **Generic climate slots (HVAC *or* temperature sensor per slot)** | `climate_hvac_count` substitution; reworked `climateN_item` handlers + tiles. Slot 1 now uses upstream's own `climate_ac_page` rework (merged 2026-08-15); slots 2/3 still run the original substitution-driven generic-slots design |
| 6 | **Climate mode dropdown + current/target temp read-back on open (bug fix)** | `on_load` blocks on `climate_ac_page` / `climate_studio_page2` / `_page3` — ported onto upstream's new `climate_ac_page` widget ids for slot 1 during the 2026-08-15 merge |
| 7 | **Per-light detail ("studio") pages for all 6 lights** | `light_studio_page` / `_page2..6` |
| 8 | **Light reset presets** | `light_reset_hue` / `_sat` / `_kelvin` / `_brightness` substitutions + per-light reset button |
| 9 | **Light colour swatches (all 6 lights)** | 12-swatch grid on `light_studio_page`/`_page2..6` (hs_color + color_temp_kelvin presets) replacing hue/sat sliders |
| 10 | **Home Screen 2 (extra 6 launcher tiles)** | `home7..12_*` substitutions, `home_page_2_title`, `home_screen_2_hide_from_navigation` |
| 11 | **Spinbox / rotary-knob cursor & reset-knob UI tweaks (minor polish)** | small edits to spinbox / encoder handlers |
| 12 | **Tap listening/thinking/replying display to cancel voice assistant** | `on_click` on the 3 VA-state pages' root `obj`, guarded by `voice_assistant.is_running`, calls `voice_assistant.stop` (same action as the existing "stop" wake word) |
| 13 | **Bigger bottom nav bar + rebalanced page layout** | `top_layer` buttonmatrix height 50→75; all 17 content-grid pages switched `align: CENTER` → `TOP_MID` + `y: ${taskbar_height}`; `page_content_height` 600→575. See in-file comments for the "why `TOP_MID`, not `CENTER`" reasoning if you resize the nav bar again |
| 14 | **ETH-2RO relay control** | `relay1_pin`/`relay2_pin` substitutions (GPIO32/GPIO46 per Waveshare's wiki), two `switch: platform: gpio` entities, repurposed `controls_page` slots 2/3 for on-panel toggle buttons — only relevant if your board has the ETH-2RO expansion fitted |
| 15 | **Screensaver returns after wake + screen-off without the screensaver** (bug fix) | touchscreen `on_release` restarts `saver_enabled`; extra screen-off branch in `saver_enabled` |

---

## 2. Detail & rationale

### 1. Voice-assistant latency + music pause/resume
Root cause of the 2–4 s wake-sound lag: the ES7210 mic (16 kHz) and ES8311 speaker
(48 kHz) share one I2S clock bus, so they **cannot run simultaneously**. The stock
wake-beep contended with the mic. Handlers were reworked so the beep no longer blocks
listening. Added `assist_button_pressed`: if the panel is playing its own audio when
the assist button is pressed, it pauses that playback (`music_paused_by_assist` global)
and auto-resumes when the assistant goes idle.

### 2–4. Media player (`media_page`)
Replaces upstream's stock media page (internal/external switcher) with a speaker picker
and a now-playing view with full-screen album art (fetched small via `album_art_resize`
and scaled up). Slot 1 is this panel (controlled on-device unless `media_target1_entity`
is set), slot 2 defaults to `external_media_player`, and Output Audio Externally selects
it; volume follows the selected speaker. Optional Music Assistant extras — library
browser, "up next", artist-photo fallback and `music_default_playlist` — are off unless
`media_music_assistant: "true"` and need the Home Assistant files in `home_assistant/`.
Setup is documented in `CONFIGURATION.md` ("Media Page"). Kept identical to the
upstream-ready `media-player-upgrade` branch.

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

### 15. Screensaver after wake + screen-off without the screensaver
`draw_display` calls `saver_enabled` before it leaves `saver_page`, so waking the panel
armed only the screen-off timer and the screensaver never came back until some unrelated
event re-ran `draw_display`; touches on other pages never restarted the countdown either.
The touchscreen's `on_release` now restarts the countdown after the page switch. Screen-off
also works with the screensaver disabled, pausing LVGL so the waking touch can't press a
button.
