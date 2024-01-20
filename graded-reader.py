import unicodedata
import re
import operator
from dataclasses import dataclass


# User may need to change the fields to suit the text being parsed
# book and chapter int may not be needed
@dataclass
class Chapter:
    book: int
    chapter: int
    new: int
    new_per: float
    text: str
    new_words: set


ACUTE = "\u0301"
GRAVE = "\u0300"
CIRCUMFLEX = "\u0342"
ACCENT = {ACUTE, GRAVE, CIRCUMFLEX}


def remove_accents(word):
    return unicodedata.normalize("NFC", "".join(
            "" if ch in ACCENT else ch
            for ch in unicodedata.normalize("NFD", word)))


def gen_set(text):
    words = set()
    p = r"\w+"
    res = re.findall(p, text)
    for word in res:
        words.add(remove_accents(word.lower()))
    return words


# Set of known words
known_set = None
# Load in known words
with open('athenaze.txt', 'r') as file:
    known_set = gen_set(file.read())


chapters = []

# Load in book to split and sort
with open('nestle1904.txt', 'r') as file:
    # These variables are only needed for texts which have numbered books and
    # chapters
    last_chap = 0
    last_book = 0
    for line in file.readlines():
        # This is for Stoffel Epitome of NT
        # if line.startswith("0") or line.startswith("title"):
        #     continue

        # Must change lines below depending on format of file
        bk, ch, rest = line.split('.', 2)
        _, text = rest.split(' ', 1)
        ibk = int(bk)
        ich = int(ch)
        # Commented code is sufficient for books which do not contain multiple
        # books within them
        # if ich > len(ch):
        if ich > last_chap or ibk > last_book:
            chapters.append(Chapter(ibk, ich, 0, 0, "", set()))
        chapters[-1].text += text
        last_chap = ich
        last_book = ibk

for i in range(len(chapters)):
    print(f"Processing chapter {i+1}/{len(chapters)}")
    for chap in chapters[i:]:
        new = 0
        num_words = 0
        new_words = set()
        new_words_norm = set()
        p = r"\w+"
        res = re.findall(p, chap.text)
        for word in res:
            if ord(word[0]) < 128:
                continue
            num_words += 1
            norm_word = remove_accents(word.lower())
            if norm_word not in known_set and norm_word not in new_words_norm:
                new += 1
                new_words.add(word)
                new_words_norm.add(norm_word)
        chap.new = new
        chap.new_per = new/num_words
        chap.new_words = new_words

    chapters[i:] = sorted(chapters[i:], key=operator.attrgetter('new_per'))
    for word in chapters[i].new_words:
        known_set.add(remove_accents(word.lower()))


# User may want to add here a list of names which corresponds to the
# book numberings to then translate back in the code below

with open("output.txt", "w") as text_file:
    for s in chapters:
        # More verbose print out:
        # out = (f"{s.text}\n# of New words: {s.new}\n"
        #        f"New word rate: {s.new_per*100}%\nNew Words:\n")
        # for w in s.new_words:
        #     out += f"{w}\n"
        # out += "\n"
        out = (f"{s.book}:{s.chapter}\n# of New words: {s.new}\n"
               f"New word rate: {s.new_per*100}%\n\n")
        text_file.write(out)
