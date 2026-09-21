# Same reason as ma_browse_fire_event.py / ma_next_track_fire_event.py:
# homeassistant.fire_event isn't available as a core action on this HA version, so
# this tiny python_script wrapper fires the ma_artist_image_updated event that
# media_artist_image.yaml's trigger-based sensor.ma_artist_image listens for.
# Call with: action: python_script.ma_artist_image_fire_event,
# data: {artist_name: "...", image_url: "..."}
hass.bus.fire("ma_artist_image_updated", data)
