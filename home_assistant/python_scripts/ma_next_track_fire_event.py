# Same reason as ma_browse_fire_event.py: homeassistant.fire_event isn't
# available as a core action on this HA version, so this tiny python_script wrapper
# fires the ma_next_track_updated event that media_next_track.yaml's
# trigger-based sensor.ma_next_track listens for.
# Call with: action: python_script.ma_next_track_fire_event, data: {next_title: "..."}
hass.bus.fire("ma_next_track_updated", data)
