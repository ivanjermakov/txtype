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

    def __str__(self):
        return " ".join(self.words)

    def __repr__(self):
        return self.__str__()

    def has_next(self):
        return len(self.words) != 0 and len(self.words) > self.current_word_index

    def next(self, word_str):
        if not self.has_next():
            raise Exception('no words left')

        current_word = self.words[self.current_word_index]
        if current_word.word_str != word_str:
            current_word.misspelled = True
        self.current_word_index += 1
        return current_word.misspelled
