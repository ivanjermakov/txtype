import curses

import text_generator
from text import Text


def _print_text(win, text):
    h, w = win.getmaxyx()

    win.erase()

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


def main(screen):
    curses.curs_set(0)
    curses.use_default_colors()
    curses.cbreak()

    curses.init_pair(1, curses.COLOR_RED, -1)  # error
    curses.init_pair(2, curses.COLOR_GREEN, -1)  # correct
    curses.init_pair(3, -1, curses.COLOR_RED)  # input error
    curses.init_pair(4, -1, curses.COLOR_GREEN)  # text complete

    h, w = screen.getmaxyx()

    # Check if screen was re-sized (True or False)
    resize = curses.is_term_resized(h, w)

    # Action in loop if resize is True:
    if resize is True:
        h, w = screen.getmaxyx()
        screen.clear()
        curses.resizeterm(h, w)

    screen.refresh()

    # TODO: pad for really huge texts
    text_win = curses.newwin(h - 1, w, 0, 0)
    text_win.refresh()

    input_win = curses.newwin(1, w - 20, h - 1, 0)
    input_win.keypad(True)
    input_win.refresh()

    status_win = curses.newwin(1, 20, h - 1, w - 20)
    status_win.addstr(f'{h}:{w}')
    status_win.refresh()

    words = text_generator.generate('resources/words.txt', 10)
    text = Text(words)

    _print_text(text_win, text)

    input_text = ''
    while True:
        key = screen.get_wch()

        # TODO: fix ctrl-v OP strategy. Disable copying and/or pasting. Or mouse actions overall
        if key == '\n' or key == ' ':
            if text.has_next():
                text.next(input_text)
            input_text = ''
        elif type(key) == str:
            input_text += key
        elif int(key) == curses.KEY_BACKSPACE:
            input_text = input_text[:-1]

        input_win.clear()

        if text.has_next():
            if input_text:
                if text.words[text.current_word_index].word_str.startswith(input_text):
                    input_win.addstr(0, 0, input_text, curses.color_pair(0))
                else:
                    input_win.addstr(0, 0, input_text, curses.color_pair(3))
        else:
            input_win.addstr('text complete', curses.color_pair(4))

            if key.lower() == 'n':
                main(screen)
            elif key.lower() == 'q':
                return

        input_win.refresh()

        _print_text(text_win, text)


curses.wrapper(main)
