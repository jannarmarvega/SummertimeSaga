## Password gate shown every time the app opens (called from label splashscreen).
## Note: this is a simple app lock, not real security; the password is stored
## in the game files.

define APP_PASSWORD = "admin"

label app_password_gate:
    $ _gate_message = "Enter password to open the app"
    scene black
    while True:
        python:
            try:
                _gate_entry = renpy.input("{b}Test App{/b}\n\n" + _gate_message, length=32, mask="*")
            except TypeError:
                _gate_entry = renpy.input("{b}Test App{/b}\n\n" + _gate_message, length=32)
        if _gate_entry.strip() == APP_PASSWORD:
            return
        $ _gate_message = "{color=#ff6060}Wrong password, try again{/color}"
