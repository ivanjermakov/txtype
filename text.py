from datetime import datetime


class Word:
    def __init__(self, word_str):
        self.word_str = word_str
        self.misspelled = False

    def __str__(self):
        return self.word_str


class Text:
    def __init__(self, word_strs):
        self.words = list(map(lambda ws: Word(ws), word_strs))
        self.current_word_index = 0
        self.start_time = None
        self.mistakes = 0
        self.correct_chars = 0
        self.percent_complete = 0
        self.percent_accuracy = 0
        self.wpm = 0
        self.cpm = 0

    def __str__(self):
        return " ".join(self.words)

    def __repr__(self):
        return self.__str__()

    def has_next(self):
        return len(self.words) != 0 and len(self.words) > self.current_word_index

    def start_typing(self):
        self.start_time = datetime.now()

    def next(self, word_str):
        if not self.has_next():
            raise Exception('no words left')

        current_word = self.words[self.current_word_index]
        if current_word.word_str != word_str:
            current_word.misspelled = True
        else:
            self.correct_chars += len(current_word.word_str)
        self.current_word_index += 1

        self.percent_complete = int((self.current_word_index / len(self.words)) * 100)

        if self.current_word_index != 0:  # zero division
            self.percent_accuracy = int(((self.current_word_index - self.mistakes) / self.current_word_index) * 100)

        if self.start_time:
            elapsed = datetime.now() - self.start_time
            elapsed_minutes = elapsed.total_seconds() / 60
            # count only correct words
            self.wpm = int((self.current_word_index - self.mistakes) / elapsed_minutes)
            self.cpm = int(self.correct_chars / elapsed_minutes)

        return current_word.misspelled
