import curses

import text_generator
from text import Text


def _init_text_win(h, w):
    # TODO: pad for really huge texts
    return curses.newwin(h - 1, w, 0, 0)


def _init_input_win(h, w):
    return curses.newwin(1, w - 24, h - 1, 0)


def _init_status_win(h, w):
    return curses.newwin(1, 24, h - 1, w - 24)


def _paint_bar(input_win, status_win, color_pair):
    input_win.bkgd(' ', color_pair)
    status_win.bkgd(' ', color_pair)
    input_win.refresh()
    status_win.refresh()


def _print_text_win(win, text):
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


def _print_input_win(win, status_win, text, input_text, key):
    h, w = win.getmaxyx()
    win.clear()

    if text.has_next():
        _paint_bar(win, status_win, curses.color_pair(0))
        win.addstr(0, 0, input_text[-w + 1:])

        if input_text:
            if not text.words[text.current_word_index].word_str.startswith(input_text):
                _paint_bar(win, status_win, curses.color_pair(3))
                win.addstr(0, 0, input_text[-w + 1:])
        win.refresh()
    else:
        _paint_bar(win, status_win, curses.color_pair(4))
        win.addstr('text complete')
        win.refresh()
        return key.lower()


def _print_status_win(win, text):
    win.clear()

    # total number of cols is 6 x 4 = 24
    complete_str = (str(text.percent_complete) + '%c')[:5]
    accuracy_str = (str(text.percent_accuracy) + '%a')[:5]
    mistakes_str = (str(text.mistakes) + 'e')[:4]
    wpm_str = (str(text.wpm) + 'wpm')[:7]
    stat_str = ' '.join([complete_str, accuracy_str, mistakes_str, wpm_str])
    win.insstr(stat_str)

    win.refresh()


def _refresh_all(screen, text_win, input_win, status_win):
    screen.refresh()
    text_win.refresh()
    input_win.refresh()
    status_win.refresh()


def _show_welcome(screen):
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
        '     w            welcome page        '
    ]

    if h > 9 and w > 38:
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

    screen.refresh()


def _show_text(screen):
    h, w = screen.getmaxyx()
    screen.refresh()

    text_win = _init_text_win(h, w)
    input_win = _init_input_win(h, w)
    status_win = _init_status_win(h, w)

    words = text_generator.generate('resources/words.txt', 10)
    text = Text(words)
    _print_text_win(text_win, text)
    _print_status_win(status_win, text)

    _refresh_all(screen, text_win, input_win, status_win)

    input_text = ''
    while True:
        key = screen.get_wch()

        if key == curses.KEY_RESIZE:
            h, w = screen.getmaxyx()
            screen.clear()
            text_win = _init_text_win(h, w)
            input_win = _init_input_win(h, w)
            status_win = _init_status_win(h, w)
            _print_text_win(text_win, text)
            _print_input_win(input_win, status_win, text, input_text, key)
            _refresh_all(screen, text_win, input_win, status_win)

        if text.current_word_index == 0 and len(input_text) == 0:
            text.start_typing()

        if key == curses.KEY_MOUSE:
            pass
        if key == '\n' or key == ' ':
            if text.has_next():
                text.next(input_text)
            input_text = ''
        elif type(key) == str:
            input_text += key
        elif int(key) == curses.KEY_BACKSPACE:
            input_text = input_text[:-1]

        _print_text_win(text_win, text)
        _print_status_win(status_win, text)

        return _print_input_win(input_win, status_win, text, input_text, key)


def main(screen):
    curses.mousemask(1)
    curses.curs_set(0)
    curses.use_default_colors()
    curses.cbreak()

    curses.init_pair(1, curses.COLOR_RED, -1)  # error
    curses.init_pair(2, curses.COLOR_GREEN, -1)  # correct
    curses.init_pair(3, -1, curses.COLOR_RED)  # input error
    curses.init_pair(4, -1, curses.COLOR_GREEN)  # text complete

    _show_welcome(screen)

    while True:
        key = screen.get_wch()
        if key == curses.KEY_RESIZE:
            _show_welcome(screen)
        elif key == 'n':
            break
        elif key == 'q':
            return

    key = _show_text(screen)
    if key:
        if key == 'n':
            _show_text(screen)
        if key == 'w':
            main(screen)
        if key == 'q':
            return


curses.wrapper(main)
