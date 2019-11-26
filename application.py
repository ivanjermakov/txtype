import curses
import os

import text_generator
from command_executor import CommandExecutor
from configuration_manager import ConfigurationManager
from text import Text


class Application:
    CONFIG_PATH = os.environ['HOME'] + '/.config/txtype/config.json'

    def __init__(self):
        self.config_manager = ConfigurationManager(self.CONFIG_PATH)
        self.executor = CommandExecutor(self.config_manager)

    def _init_text_win(self, h, w):
        # TODO: pad for really huge texts
        return curses.newwin(h - 1, w, 0, 0)

    def _init_input_win(self, h, w):
        return curses.newwin(1, w - 24, h - 1, 0)

    def _init_status_win(self, h, w):
        return curses.newwin(1, 24, h - 1, w - 24)

    def _init_command_win(self, h, w):
        return curses.newwin(1, w, h - 1, 0)

    def _init_result_win(self, h, w):
        return curses.newwin(1, w, h - 2, 0)

    def _paint_bar(self, input_win, status_win, color_pair):
        input_win.bkgd(' ', color_pair)
        status_win.bkgd(' ', color_pair)
        input_win.refresh()
        status_win.refresh()

    def _print_text_win(self, win, text):
        h, w = win.getmaxyx()

        win.clear()

        for i, word in enumerate(text.words):
            w_s = str(word)
            y, x = win.getyx()

            if w - 1 < x + len(w_s):
                win.addstr('\n')

            if i == text.current_word_index:
                win.addstr(w_s, curses.A_UNDERLINE)
            elif i >= text.current_word_index:
                win.addstr(w_s)
            else:
                if word.misspelled:
                    win.addstr(w_s, curses.color_pair(1))
                else:
                    win.addstr(w_s, curses.color_pair(2))

            if i != len(text.words) - 1:
                win.addstr(' ')

        win.refresh()

    def _print_input_win(self, win, status_win, text, input_text, key):
        h, w = win.getmaxyx()
        win.clear()

        if text.has_next():
            self._paint_bar(win, status_win, curses.color_pair(0))
            win.addstr(0, 0, input_text[-w + 1:])

            if input_text:
                if not text.words[text.current_word_index].word_str.startswith(input_text):
                    self._paint_bar(win, status_win, curses.color_pair(3))
                    win.addstr(0, 0, input_text[-w + 1:])
            win.refresh()
        else:
            self._paint_bar(win, status_win, curses.color_pair(4))
            win.addstr('text complete')
            win.refresh()
            return key

    def _print_status_win(self, win, text):
        win.clear()

        # total number of cols is 6 x 4 = 24
        complete_str = (str(text.percent_complete) + '%c')[:5]
        accuracy_str = (str(text.percent_accuracy) + '%a')[:5]
        mistakes_str = (str(text.mistakes) + 'e')[:4]
        wpm_str = (str(text.wpm) + 'wpm')[:7]
        stat_str = ' '.join([complete_str, accuracy_str, mistakes_str, wpm_str])
        win.insstr(stat_str)

        win.refresh()

    def _refresh_all(self, screen, text_win, input_win, status_win):
        screen.refresh()
        text_win.refresh()
        input_win.refresh()
        status_win.refresh()

    def _command_view(self, screen):
        h, w = screen.getmaxyx()

        command = ':'

        command_win = self._init_command_win(h, w)
        command_win.clear()
        command_win.addstr(command)
        command_win.refresh()

        result_win = self._init_result_win(h, w)
        result_win.refresh()

        while True:
            ch = screen.get_wch()

            if ch == curses.KEY_BACKSPACE:
                if len(command) > 1:
                    command = command[:-1]
                else:
                    command_win.clear()
                    command_win.refresh()
                    break
            elif ch == '\n':
                result = str(self.executor.execute(command[1:]))

                if result:
                    result_win.addstr(result)
                    result_win.refresh()

                command_win.clear()
                command_win.refresh()
                break
            if type(ch) == str:
                command += ch

            command_win.clear()
            command_win.addstr(command)
            command_win.refresh()

    def _welcome_view(self, screen):
        h, w = screen.getmaxyx()

        screen.clear()

        lines = [
            '          Welcome to TXTYPE!          ',
            '                                      ',
            '     Command line typing software     ',
            'https://github.com/ivanjermakov/txtype',
            '                                      ',
            'Help:                                 ',
            '     ctrl+z       force exit          ',
            '     q            exit                ',
            '     n            next text           ',
            '     w            welcome page        ',
            '     :            enter command       ',
        ]

        if h > 10 and w > 37:
            y = h // 2 - len(lines) // 2
            x = w // 2 - len(lines[0]) // 2

            for i, l in enumerate(lines):
                screen.insstr(y + i, x, l)

            # accents
            screen.addstr(y, x + 21, 'TXTYPE', curses.color_pair(2))
            screen.addstr(y + 6, x + 5, 'ctrl+z', curses.color_pair(2))
            screen.addstr(y + 7, x + 5, 'q', curses.color_pair(2))
            screen.addstr(y + 8, x + 5, 'n', curses.color_pair(2))
            screen.addstr(y + 9, x + 5, 'w', curses.color_pair(2))
            screen.addstr(y + 10, x + 5, ':', curses.color_pair(2))

        screen.refresh()

        while True:
            key = screen.get_wch()

            if key == curses.KEY_RESIZE:
                self._welcome_view(screen)
                return
            if key == 'n':
                self._text_view(screen)
                return
            if key == ':':
                self._command_view(screen)
            if key == 'q':
                return

    def _text_view(self, screen):
        h, w = screen.getmaxyx()

        text_win = self._init_text_win(h, w)
        input_win = self._init_input_win(h, w)
        status_win = self._init_status_win(h, w)

        words = text_generator.generate(
            self.config_manager.config.get_param('active_dictionary'),
            int(self.config_manager.config.get_param('text_words_count'))
        )
        text = Text(words)
        self._print_text_win(text_win, text)
        self._print_status_win(status_win, text)

        self._refresh_all(screen, text_win, input_win, status_win)

        input_text = ''
        while True:
            key = screen.get_wch()

            # TODO: refactor
            if key == curses.KEY_RESIZE:
                h, w = screen.getmaxyx()
                screen.clear()
                text_win = self._init_text_win(h, w)
                input_win = self._init_input_win(h, w)
                status_win = self._init_status_win(h, w)
                self._print_text_win(text_win, text)
                self._print_input_win(input_win, status_win, text, input_text, key)
                self._refresh_all(screen, text_win, input_win, status_win)

            if text.current_word_index == 0 and len(input_text) == 0:
                text.start_typing()

            if key == '\n' or key == ' ':
                if text.has_next():
                    text.next(input_text)
                input_text = ''
            elif type(key) == str:
                input_text += key
            elif int(key) == curses.KEY_BACKSPACE:
                input_text = input_text[:-1]

            self._print_text_win(text_win, text)
            self._print_status_win(status_win, text)

            key = self._print_input_win(input_win, status_win, text, input_text, key)

            if not key:
                continue

            if key == 'n':
                self._text_view(screen)
                return
            if key == 'w':
                self._welcome_view(screen)
                return
            if key == ':':
                self._command_view(screen)
                self._print_status_win(status_win, text)
                self._print_input_win(input_win, status_win, text, input_text, key)
            if key == 'q':
                return

    def main(self, screen):
        curses.mousemask(1)
        curses.curs_set(0)
        curses.use_default_colors()

        curses.init_pair(1, curses.COLOR_RED, -1)  # error
        curses.init_pair(2, curses.COLOR_GREEN, -1)  # correct
        curses.init_pair(3, -1, curses.COLOR_RED)  # input error
        curses.init_pair(4, -1, curses.COLOR_GREEN)  # text complete

        self._welcome_view(screen)

    def start(self):
        curses.wrapper(self.main)
