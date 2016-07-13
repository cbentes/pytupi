import json


class ConfigManager:

    def __init__(self, config_file):
        self._config_file = config_file
        self._configurations = None

    def get_config(self, config_key):
        if self._configurations is None:
            self._load_config()
        return self._configurations[config_key]

    def _load_config(self):
        self._configurations = {}
        with open(self._config_file, 'r') as f:
            json_data = f.read()
            self._configurations = json.loads(json_data)

    def has_config_key(self, config_key):
        if self._configurations is None:
            self._load_config()
        return config_key in self._configurations
