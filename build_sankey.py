
from extract_data import associations_for_episodes


DEFAULT_RESTRICT_CHARS = {'ZEHIRMANN', 'TRICHELIEU', 'ENORIEL', 'WRANDRALL', 'NARRATEUR', 'ZARAKAÏ', 'DRAGONNE', 'ROGER', 'KYO'}
DEFAULT_IGNORE_CHARS = {'TOUS', 'VOIX', 'GARS', 'GARS 2', 'GROUPE'}
DEFAULT_TITLE = "Timeline des personnages de Reflets d'Acide"


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


def next_chapter_of_chapter(all_chapters:tuple) -> dict:
    """return map {chapter uid: {chapter_uid}}
    indicating the following chapters of the key chapter.

    A chapter is next to another if it is the first among following
    ones that reference a character.

    """
    for episode, chapters in all_chapters:
        for chapter, characters in chapters:
            successors = tuple(found_nexts_of(all_chapters, episode, chapter, characters))
            # print(f'\tSUCCESSORS of {pretty_chapter_uid(episode, chapter)}: {successors}')
            yield (episode, chapter), set(successors)


def found_nexts_of(all_chapters:tuple, prev_episode:int, prev_chapter:int, prev_characters:set):
    """Return pair (chapter, overlap), where chapter is a pair (episode number, chapter number),
    and overlap is the set of characters shared between the returned chapter
    and the previous chapter given as (prev_episode, prev_chapter).

    """
    prev_characters = set(prev_characters)
    for episode_nb, chapters in all_chapters:
        for chapter_nb, characters in chapters:
            if not prev_characters: break  # no more possible successors
            if (episode_nb, chapter_nb) <= (prev_episode, prev_chapter): continue  # too soon
            # print(f'SEARCHING: next of {pretty_chapter_uid(prev_episode, prev_chapter)} searched in {pretty_chapter_uid(episode_nb, chapter_nb)}…')
            overlap = prev_characters & characters
            if overlap:  # there is an overlap !
                prev_characters -= characters
                # print(f'\tOVERLAP BETWEEN {prev_episode}/{prev_chapter} and {episode_nb}/{chapter_nb} on {"/".join(overlap)}')
                yield (episode_nb, chapter_nb), frozenset(overlap)


def pretty_list_of_chapters(all_chapters:tuple):
    "Maps function pretty_chapter_uid on all given chapters"
    for episode, chapters in all_chapters:
        for chapter, _ in chapters:
            yield pretty_chapter_uid(episode, chapter)

def build_links(all_chapters:tuple) -> [(int, int, int, str)]:
    "Yield for each chapter all the following chapters and their overlap"
    for chapter, followers in next_chapter_of_chapter(all_chapters):
        for successor, chars in followers:
            yield chapter, successor, len(chars), ', '.join(chars)


def make_sankey_chart(labels, sources, targets, values, descs, title:str=DEFAULT_TITLE, black_theme:bool=False):
    import plotly
    import plotly.graph_objs as go

    data = {
        'type': 'sankey',
        'node': {
            'pad': 15,
            'thickness': 3,
            'line': {'color': 'black'},
            'label': labels,
        },
        'link': {
            'source': sources,
            'target': targets,
            'value': values,
            'label': descs,
        }
    }
    layout = {'title': title, 'font': {'size': 12}}
    if black_theme:
        layout.update({
            'plot_bgcolor': 'black',
            'paper_bgcolor': 'black',
        })
        layout['font']['color'] = 'white'
    fig = {'data': [data], 'layout': layout}
    plotly.offline.plot(fig, auto_open=False)


def sankey_chart_for_episodes(episodes:range=range(1, 17), ignore_chars:set=set(), restrict_chars:set=None, **kwargs) -> dict:
    chapter_to_chars = tuple(associations_for_episodes(episodes, ignore_chars=ignore_chars, restrict_chars=restrict_chars))
    chart_labels = tuple(pretty_list_of_chapters(chapter_to_chars))
    chart_labels_index = {l: i for i, l in enumerate(chart_labels)}
    all_characters = set.union(*(
        characters
        for episode_nb, chapters in chapter_to_chars
        for chapter_nb, characters in chapters
    ))
    from pprint import pprint
    print('ALL CHARS:')
    pprint(all_characters)
    # print()
    # print(chapter_to_chars)
    # print('LABELS:', chart_labels)
    # print(tuple(next_chapter_of_chapter(chapter_to_chars)))
    sources, targets, values, descs = zip(*build_links(chapter_to_chars))
    # map sources and targets to their index in the labels list
    sources = tuple(chart_labels_index[pretty_chapter_uid(*source)] for source in sources)
    targets = tuple(chart_labels_index[pretty_chapter_uid(*target)] for target in targets)
    # make the chart
    make_sankey_chart(chart_labels, sources, targets, values, descs, **kwargs)


if __name__ == "__main__":
    # RESTRICT_CHARS = None
    sankey_chart_for_episodes(range(6, 12), ignore_chars=DEFAULT_IGNORE_CHARS, restrict_chars=DEFAULT_RESTRICT_CHARS)
