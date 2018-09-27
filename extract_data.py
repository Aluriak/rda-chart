
import re
import math
import itertools
from operator import itemgetter
from collections import defaultdict, namedtuple
from definitions import CHAR_ALIASES, PATH_TEMPLATE

CHAPTER_HEAD = 'Chapitre '
REG_CHAPTER = re.compile(r"Chapitre ([0-9]+) - (.+)$")
REG_CHARACTER = re.compile(r"([A-Z0-9ÉÈÊÀÄÂÔÛÏ.,!?' -]+) : ?")


Chapter = namedtuple('Chapter', 'episode, chapter, name, characters')


def pretty_chapter_uid(episode:int, chapter:int) -> str:
    """

    >>> pretty_chapter_uid(1, 1)
    'E01C01'
    >>> pretty_chapter_uid(4, 78)
    'E04C78'
    >>> pretty_chapter_uid(13, 42)
    'E13C42'
    >>> pretty_chapter_uid(130, 420)
    'E130C420'

    """
    return f"E{str(episode).rjust(2, '0')}C{str(chapter).rjust(2, '0')}"


def character_in_line(line:str) -> str:
    return line.split(':', 1)[0]


def read_episode_files(episodes:range=range(1, 17)) -> [(int, str)]:
    "Yield pairs (episode number, episode full-text)"
    def open_episode(path:str) -> [str]:
        with open(path) as fd:
            return fd.readlines()

    for nb in episodes:
        yield nb, tuple(open_episode(PATH_TEMPLATE.format(nb)))


def gen_characters_per_chapter(text:str, ignore_chars:set=set(), restrict_chars:set=None) -> [(int, set)]:
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
                new_char = CHAR_ALIASES.get(new_char, new_char)
                if restrict_chars and new_char in restrict_chars:
                    characters.add(new_char)
                elif not restrict_chars and new_char not in ignore_chars:
                    characters.add(new_char)
    if chapter_nb is not None and characters:  # there was a previous chapter, and it contained characters
        yield chapter_nb, characters


# def iter_over_chapters(episode_chapters:[(int, [(int, set)])], start_episode:int=1, start_chapter:int=1) -> [(int, int, set)]:
    # "Yield 3-uplet (episode_nb, chapter_nb, characters) for each chapter of each episode, starting with given one"
    # for episode_nb, chapters_chars in episode_chapters:
        # for chapter_nb, chars in chapters_chars:
            # if (episode_nb, chapter_nb) > (start_episode, start_chapter):
                # yield episode_nb, chapter_nb, chars

def merge_identical_chapters(episodes_chapters:[Chapter]) -> [Chapter]:
    """Merge (non-immediatly) consecutive chapters having the same characters"""
    episodes_chapters = tuple(episodes_chapters)
    merged_chapters = set()

    for episode_nb, chapter_nb, chapter_name, characters in episodes_chapters:
        if chapter_name in merged_chapters: continue  # this chapter was merged
        identicals = set()
        # determine which chapters can be merged with `chapter_name`
        for next_episode_nb, next_chapter_nb, next_name, next_chars in episodes_chapters:
            if (episode_nb, chapter_nb) >= (next_episode_nb, next_chapter_nb): continue  # ignore previous
            same_characters = next_chars == characters
            character_overlap = next_chars & characters
            if character_overlap and not same_characters:
                break  # no merge remaining
            elif same_characters:  # let's merge
                identicals.add(next_name)
            merged_chapters |= identicals
        # the merged chapters disapears, but leave a trace in the name of the kept ones.
        complete_name = chapter_name + (('/' + '/'.join(identicals)) if identicals else '')
        yield Chapter(episode_nb, chapter_nb, complete_name, characters)


def associations_for_episodes(episodes:range=range(1, 17), ignore_chars:set=set(), restrict_chars:set=None) -> [Chapter]:
    """Yield Chapter instances found in given episodes"""
    iter_episodes = read_episode_files(episodes)
    for episode, text in iter_episodes:
        chapters = gen_characters_per_chapter(text, ignore_chars, restrict_chars)
        chapters = tuple(chapters)
        # print('CHAPTERS:', chapters)
        # print(f"CHAPTERS: Épisode {episode}, chapitres {min(chapters)[0]} à {max(chapters)[0]}")
        for chapter, chars in chapters:
            print(f"CHAPTER: Épisode {episode}, chapitre {chapter} avec {chars}")
            yield episode, chapter, pretty_chapter_uid(episode, chapter), chars


def add_io_chapters(chapter_to_chars:[Chapter], all_characters) -> [Chapter]:
    "Add chapters before and after given ones that introduce and conclude each given character"
    for idx, char in enumerate(all_characters, start=1):
        yield Chapter(0, idx, char+'>', {char})
    yield from chapter_to_chars
    for idx, char in enumerate(all_characters, start=1):
        yield Chapter(math.inf, idx, '<'+char, {char})


if __name__ == '__main__':
    (tuple(associations_for_episodes()))
