# Changes on top of upstream `esphome-p4-86-panel-eth-2ro-lvgl`

**Base version:** forked from upstream tag **`2026.07.02`**, then merged forward onto
upstream `main` @ `a090b2e` (2026-07-31) on 2026-08-15 and `1c5132f` (`2026.09.17`) on
2026-09-21 — this branch tracks the latest upstream revisions plus the features below.
**Upstream:** https://github.com/chrisdunnname/esphome-p4-86-panel-eth-2ro-lvgl
**This branch's file:** `esp32-p4-86-panel.yaml` (same filename as upstream — this is a
personal fork branch, not a PR submission; see "Status" below).

This document summarises every change made on top of the stock firmware and where each
change lives. It follows this
repo's own `CONTRIBUTING.md` guidance: features are commented in-file (search for
`[FORK]`) and described here so they can, where practical, be isolated / included /
excluded by others.

**Status:** this is a personal fork, published for visibility/reference. No PR has been
opened against upstream. The media player (#2–4 below) is also kept as a standalone,
upstream-ready branch, `media-player-upgrade`, containing only that change. Feel free to
cherry-pick anything useful; the feature table below is meant to make that easy without
having to read the whole diff.

---

## 1. Feature summary

| # | Feature | New IDs / substitutions |
|---|---------|-------------------------|
| 1 | **Voice-assistant wake-sound latency fix + assist-button music pause/resume** | `assist_button_pressed` script, `music_paused_by_assist` global, reworked `voice_assistant` `on_end`/`on_idle`/`on_play` handlers |
| 2–4 | **Media player: speaker picker, now-playing with album art, optional Music Assistant extras** (replaces the stock media page; same as branch `media-player-upgrade`) | `media_page` (rebuilt), `library_browse_page`, `media_set_page`; `media_target_count`, `media_target1..8_name`/`_entity`, `media_music_assistant`, `music_default_playlist`, `album_art_resize` substitutions; `apply_media_target` / `refresh_np` scripts; Home Assistant side in `home_assistant/` |
| 5 | **Generic climate slots (HVAC *or* temperature sensor per slot)** | `climate_hvac_count` substitution; reworked `climateN_item` handlers + tiles. Slot 1 now uses upstream's own `climate_ac_page` rework (merged 2026-08-15); slots 2/3 still run the original substitution-driven generic-slots design |
| 6 | **Climate mode dropdown + current/target temp read-back on open (bug fix)** | `on_load` blocks on `climate_ac_page` / `climate_studio_page2` / `_page3` — ported onto upstream's new `climate_ac_page` widget ids for slot 1 during the 2026-08-15 merge |
| 7 | **Per-light detail ("studio") pages for all 6 lights** | `light_studio_page` / `_page2..6`; hold a light tile on the lights page (≥500 ms, `light_press_ms` global) to open its page; `lightN_item` binary sensors keep both pages' buttons in sync |
| 8 | **Light reset presets** | `light_reset_hue` / `_sat` / `_kelvin` / `_brightness` substitutions + per-light reset button (`but_lightresetN`) |
| 9 | **Light colour swatches (all 6 lights)** | 12-swatch grid on `light_studio_page`/`_page2..6` (hs_color + color_temp_kelvin presets) replacing hue/sat sliders |
| 10 | **Home Screen 2 (extra 6 launcher tiles)** | `home7..12_*` substitutions, `home_page_2_title`, `home_screen_2_hide_from_navigation` |
| 11 | **Climate spinbox polish** | climate target-temperature spinboxes are set only with their +/- buttons (`clickable: false`) and hide the selected-digit cursor |
| 12 | **Tap listening/thinking/replying display to cancel voice assistant** | `on_click` on the 3 VA-state pages' root `obj`, guarded by `voice_assistant.is_running`, calls `voice_assistant.stop` (same action as the existing "stop" wake word) |
| 13 | **Bigger bottom nav bar + rebalanced page layout** | `top_layer` buttonmatrix height 50→75; all 17 content-grid pages switched `align: CENTER` → `TOP_MID` + `y: ${taskbar_height}`; `page_content_height` 600→575. See in-file comments for the "why `TOP_MID`, not `CENTER`" reasoning if you resize the nav bar again |
| 14 | **ETH-2RO relay control** | `relay1_pin`/`relay2_pin` substitutions (GPIO32/GPIO46 per Waveshare's wiki), two `switch: platform: gpio` entities, repurposed `controls_page` slots 2/3 for on-panel toggle buttons — only relevant if your board has the ETH-2RO expansion fitted |
| 15 | **Screensaver returns after wake + screen-off without the screensaver** (bug fix) | touchscreen `on_release` restarts `saver_enabled`; extra screen-off branch in `saver_enabled` |
| 16 | **Voice assistant no longer waits on / reboots over normal music playback** (bug fix) | `voice_assistant` `on_end`: wait and forced-reboot check use `media_player.is_announcing` only |

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
Replaces upstream's stock media page, which could only control this panel or one external
player (switched by a hidden toggle) and showed no track details. Kept identical to the
upstream-ready `media-player-upgrade` branch; setup is documented in `CONFIGURATION.md`
("Media Page") and the new settings entities in `USAGE.md`.

**Compatibility.** Keeps the page id `media_page` and the `media_page_title` /
`media_page_hide_from_navigation` substitutions, so existing configs and home-screen tiles
keep working. `media_page_hide_switcher` is removed (the speaker picker replaces the
switcher). This fork's earlier second page, `media_control_page`, is merged into it.

**Speaker picker.** A dropdown at the top of the controls selects what the page controls.
`media_target_count` (1–8, default `2`) sets how many slots are offered; the dropdown is
trimmed to that many at boot and hidden when it is 1. Slot 1 is always this panel: with
`media_target1_entity` left as `media_player.none` it is controlled on-device (play/pause,
stop, volume, mute — no track details or previous/next); set it to this panel's own Home
Assistant / Music Assistant player to get those too. Slot 2 defaults to
`external_media_player`, and turning *Output Audio Externally* on or off selects slot 2 or
slot 1, mirroring the old switcher.

**Controls.** Play/pause, previous, next, stop, volume and mute, docked in a compact grid at
the bottom so the middle of the screen is free for the artwork. Controls respond to a tap
(upstream's other pages use long-press) because transport controls are used repeatedly.
Volume follows the selected speaker (slot 1 also sets the voice assistant's volume); mute
is only offered for this panel.

**Now playing.** Title and artist of the selected speaker, over full-screen album art that
is fetched small (`album_art_resize`, default 256×256) and scaled up with a dimming scrim,
keeping downloads and JPEG decoding light on the main loop. Art is only fetched while the
page is visible; overlapping fetches are deduplicated and a failed fetch retries once.

**Media settings.** Settings > Media (long press): *Hide Speaker Selection*, *Playback
Device* (same picker) and, with the Music Assistant extras, *Show Up Next* and *Show
Library Browser*. Each is also a Home Assistant config entity.

**Music Assistant extras (optional, `media_music_assistant: "true"`).**
- **Library browser** (`library_browse_page`): Artists / Albums / Playlists / Tracks in
  pages of six, drill-down with a back button, an A–Z jump strip and a play button per row.
- **Up next:** the next queued track, shown under the current one.
- **Artist photo:** used when a track or album has no artwork of its own.
- **Default playlist:** `music_default_playlist` starts when play is pressed with nothing
  queued (a paused track resumes as normal).

These need a Home Assistant side, in `home_assistant/`: three packages (template sensors
and scripts that call Music Assistant and return results by event) and three one-line
`python_scripts` that fire those events, with `python_script:` enabled. *Music Library:
Fix Sorting* (`input_boolean.ma_browse_fix_library_sort`) re-sorts the library by displayed
name instead of Music Assistant's internal sort name (slower on large libraries, off by
default). The browse state is shared by every panel using the packages, so two panels
browsing at the same moment show the same list.

**Notes.** Both speaker pickers use `on_change` (user taps only): since ESPHome 2026.9 a
programmatic dropdown update also fires `on_value`. Each speaker slot adds four Home
Assistant text sensors that re-run `refresh_np`, which adds some main-loop load on a busy
panel.

### 5–6. Generic climate slots + read-back on open
`climate_hvac_count` (default `3`) sets how many climate slots are HVAC units
(`climate.*`); the remaining slots become read-only temperature sensors (`sensor.*`).
Slot 1 was independently reworked by the upstream author (2026-07-31, commit
`9a8b6fc`) into a nicer native-spinbox UI (`climate_ac_page`); that rework was missing
two bug fixes from this branch (stale mode-dropdown / stale current-temp on page open),
which were ported onto the new widget ids during the 2026-08-15 merge. Slots 2/3 are
untouched by upstream and still run the original substitution-driven generic-slots
design.

### 7–8. Light detail pages + reset presets
Each of the six lights gets its own detail page with brightness, colour and a reset button.
On the lights page a tap still toggles the light; holding a tile for at least 500 ms opens
its detail page instead. The reset button returns the light to a configurable white
(`light_reset_kelvin`, `light_reset_brightness`; `light_reset_hue`/`_sat` for the white
point).

### 9. Light colour swatches
Replaces the clunky hue/sat sliders with a tappable 12-swatch grid (6 saturated colours,
purple/pink/magenta, and 3 white colour-temperatures), applied to all six light detail
pages. Each light's `lightN_hscolor` sensor's slider-sync `on_value` is neutralised (the
sliders no longer exist).

### 10. Home Screen 2
A second launcher page with six more tiles (`home7..12_*`, same format as the first home
screen). It joins the swipe cycle only when `home_screen_2_hide_from_navigation` is
`false`, so it stays out of the way when unused.

### 11. Climate spinbox polish
The target-temperature spinboxes are changed only with their +/- buttons, so an accidental
tap on the number can't start digit editing, and the selected-digit highlight is hidden so
the value reads as plain text.

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

### 16. Voice-assistant forced reboot during music
Upstream's `on_end` safety net waits for audio to finish and (with `voice_assistant_reboot`
on) reboots if it is still going, to unstick a wedged announcement on the shared I2S bus.
It also checked `media_player.is_playing`, which can't tell a stuck announcement from music
playing normally, so a voice command during music held `on_end` for the full timeout and
could reboot the panel. Both checks now look at announcements only.
