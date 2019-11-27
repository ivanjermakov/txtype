import os

from configuration import Configuration


class ConfigurationManager:
    def __init__(self, path, create):
        self.path = path

        dir_path = path[:path.rfind('/')]
        if not os.path.exists(path):
            if create:
                os.makedirs(dir_path, exist_ok=True)
                self.config = Configuration()
                self.write()
            else:
                raise IOError(f'configuration file "{path}" not found. Use flag --new to create new configuration file')

        self.config = self.read()

    def write(self):
        with open(self.path, 'w') as f:
            f.write(self.config.dump())

    def read(self):
        with open(self.path) as f:
            return Configuration.load(f.read())
