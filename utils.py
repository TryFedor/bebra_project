import json

def load_settings(module=None):
    if module is None:
        settings = json.load(open('settings.json'))

        return settings
