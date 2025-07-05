# answers.txt credit: https://roy-orbison.github.io/wordle-guesses-answers/
with open("./answers.txt") as f:
    WORDS = [w.strip() for w in f.readlines() if w]

WORD_IDS = {w: i for i, w in enumerate(WORDS)}
