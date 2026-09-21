# homeassistant.fire_event isn't available as a core action on this HA version
# (confirmed live: "Action homeassistant.fire_event not found"). python_script is already
# enabled in your Home Assistant, so this tiny wrapper fires the ma_browse_updated event that
# music_library_browser.yaml's trigger-based sensor.ma_browse_state listens for.
# Call with: action: python_script.ma_browse_fire_event, data: <the event payload dict>
hass.bus.fire("ma_browse_updated", data)
