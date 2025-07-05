# answers.txt credit: https://roy-orbison.github.io/wordle-guesses-answers/
from collections import Counter

with open("./answers.txt") as f:
    WORDS = [w.strip() for w in f.readlines() if w]

_FREQUENCIES: Counter = Counter()

for word in WORDS:
    _FREQUENCIES.update(word)


def _score(word):
    """Custom scoring function for guesses: we prioritize words with as many
    distinct characters as possible, and then the ones with the most frequent
    letters"""

    no_distinct = len(set(word))
    freq_score = sum(_FREQUENCIES[c] for c in word)
    return (no_distinct, freq_score)


WORDS = sorted(WORDS, key=_score)
WORD_IDS = {w: i for i, w in enumerate(WORDS)}
