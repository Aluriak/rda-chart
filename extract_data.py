
import re
from collections import defaultdict


PATH_TEMPLATE = './sagas-mp3/Reflets/Textes/Reflets-{}.html'
CHAPTER_HEAD = 'Chapitre '
REG_CHAPTER = re.compile(r"Chapitre ([0-9]+) - ([a-zA-Z0-9ÉÈÊÀÂÔÛéèêàâôùûîïüç«».,!?'\"()  -]+)$")
REG_CHARACTER = re.compile(r"([A-Z0-9ÉÈÊÀÄÂÔÛÏ.,!?' -]+) : ?")

# assert 'L'enrôlement au « feu »'


def character_in_line(line:str) -> str:
    return line.split(':', 1)[0]


def read_episode_files(episodes:range=range(1, 17)) -> [(int, str)]:
    "Yield pairs (episode number, episode full-text)"
    def open_episode(path:str) -> [str]:
        with open(path) as fd:
            return fd.readlines()

    for nb in episodes:
        yield nb, tuple(open_episode(PATH_TEMPLATE.format(nb)))


def gen_characters_per_chapter(text:str, ignore_chars:set=set(), restrict_chars:set=None) -> [set]:
    "Yield {characters in chapter} for each chapter found in given episode"
    line, prev_line, text = None, None, iter(text)
    chapter_nb, characters = None, set()
    # skip episode title
    next(text)
    # now parse the full file
    while True:
        try:
            prev_line, line = line, next(text).strip()
        except StopIteration:
            break
        if not prev_line:
            if line.startswith(CHAPTER_HEAD):
                match = REG_CHAPTER.fullmatch(line)
                if match is None:
                    print(f"ERROR: chapter '{line}' is not matched by regex.")
                    chapter_nb, chapter_title = 0, 'unknow'
                else:
                    if chapter_nb is not None and characters:  # there was a previous chapter, and it contained characters
                        yield chapter_nb, characters
                    chapter_nb, chapter_title = match.groups(0)
                chapter_nb, chapter_title = int(chapter_nb), chapter_title.strip()
                characters = set()
        else:  # it may be a line starting with a character name
            match = REG_CHARACTER.match(line)
            if match:
                new_char = match.groups(0)[0].strip()
                if restrict_chars and new_char in restrict_chars:
                    characters.add(new_char)
                elif not restrict_chars and new_char not in ignore_chars:
                    characters.add(new_char)
    if chapter_nb is not None and characters:  # there was a previous chapter, and it contained characters
        yield chapter_nb, characters


def associations_for_episodes(episodes:range=range(1, 17), ignore_chars:set=set(), restrict_chars:set=None) -> dict:
    """Yield pairs (episode number, chapters), where chapter is an iterable
    of pair (chapter number, characters present in chapter)"""
    iter_episodes = read_episode_files(episodes)
    for episode, text in iter_episodes:
        chapters = tuple(gen_characters_per_chapter(text, ignore_chars, restrict_chars))
        print(f"CHAPTERS: Épisode {episode}, chapitres {min(chapters)[0]} à {max(chapters)[0]}")
        yield episode, chapters


if __name__ == '__main__':
    (tuple(associations_for_episodes()))
