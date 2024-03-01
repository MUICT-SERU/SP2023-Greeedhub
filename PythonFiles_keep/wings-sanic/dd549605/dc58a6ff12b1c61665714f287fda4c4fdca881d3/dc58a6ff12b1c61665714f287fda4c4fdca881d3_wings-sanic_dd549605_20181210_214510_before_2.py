import json
import os

from wings_sanic import application, settings

# -----------  dev settings -------------
dev_settings = {
    'BLUEPRINTS': [
        'bp_a.bp'
    ]
}
settings.load(**dev_settings)

# ----------- use config that is from environ to cover dev_settings ----------
config_json = os.environ.get('CONFIG', '')
if config_json:
    try:
        conf = json.loads(config_json)
        if conf and isinstance(conf, dict):
            settings.load(**conf)
    except:
        pass

# --------------------- main -----------------
if __name__ == '__main__':
    application.start()
