import json

CONFIG_TEMPLATE = {
    'dictionaries': [],
    'active_dictionary': None,
    'text_words_count': None,
}

DEFAULT = CONFIG_TEMPLATE
DEFAULT['dictionaries'] = [
    'resources/words.txt',
    'resources/words_ru.txt'
]
DEFAULT['active_dictionary'] = DEFAULT['dictionaries'][0]
DEFAULT['text_words_count'] = 10


class Configuration:
    config = DEFAULT

    def set_param(self, param, value=None):
        # TODO: type check parameter value (scalar/list)
        if param not in CONFIG_TEMPLATE.keys():
            return f'unknown parameter "{param}"'

        if value:
            self.config[param] = value
            return f'set parameter "{param}" to "{value}"'
        else:
            self.config[param] = CONFIG_TEMPLATE[param]
            return f'set parameter "{param}" to default "{CONFIG_TEMPLATE[param]}"'

    def dump(self):
        return json.dumps(self.config, indent=4)

    def write(self, path):
        string = self.dump()
        with open(path, 'w') as f:
            f.write(string)

    @staticmethod
    def load(json_string):
        config = Configuration()
        config.config = json.loads(json_string)
        return config

    @staticmethod
    def read(path):
        with open(path) as f:
            config = Configuration()
            config.config = Configuration.load(f.read())
            return config
