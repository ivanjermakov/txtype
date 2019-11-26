import os

import configuration


class ConfigurationManager:
    def __init__(self, path):
        self.path = path

        dir_path = path[:path.rfind('/')]
        if not os.path.exists(path):
            os.makedirs(dir_path)
            self.config = configuration.DEFAULT
            self.write()

        self.config = self.read()

    def write(self):
        with open(self.path, 'w') as f:
            f.write(self.config.dump())

    def read(self):
        with open(self.path) as f:
            return configuration.Configuration.load(f.read())
