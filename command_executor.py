class CommandExecutor:
    def __init__(self, config_manager):
        self.config_manager = config_manager

    def execute(self, command):
        command = command.strip()
        words = command.split()

        if len(words) == 0:
            return 'no command provided'

        group = words[0]
        args = words[1:]
        if group == 'show':
            return self._show(args)
        elif group == 'set':
            return self._set(args)
        return f'unknown command "{group}"'

    def _show(self, words):
        if len(words) == 0:
            return 'no parameter provided'

        param_name = words[0]
        param_value = self.config_manager.config.config.get(param_name)
        if param_value:
            return param_value
        else:
            return f'unknown parameter "{param_name}"'

    def _set(self, words):
        if len(words) == 0:
            return 'no parameter provided'

        param_name = words[0]
        result = self.config_manager.config.set_param(param_name, words[1] if len(words) >= 2 else None)
        self.config_manager.write()
        return result
