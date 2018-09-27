
from pprint import pprint
from extract_data import associations_for_episodes, merge_identical_chapters, pretty_chapter_uid, add_io_chapters
from definitions import DEFAULT_TITLE



def next_chapter_of_chapter(all_chapters:tuple) -> dict:
    """return map {chapter uid: {chapter_uid}}
    indicating the following chapters of the key chapter.

    A chapter is next to another if it is the first among following
    ones that reference a character.

    """
    for episode, chapter, name, characters in all_chapters:
        successors = tuple(found_nexts_of(all_chapters, episode, chapter, characters))
        # print(f'\tSUCCESSORS of {pretty_chapter_uid(episode, chapter)}: {successors}')
        yield name, set(successors)


def found_nexts_of(all_chapters:tuple, prev_episode:int, prev_chapter:int, prev_characters:set):
    """Return pair (chapter, overlap), where chapter is a pair (episode number, chapter number),
    and overlap is the set of characters shared between the returned chapter
    and the previous chapter given as (prev_episode, prev_chapter).

    """
    prev_characters = set(prev_characters)
    for episode_nb, chapter_nb, name, characters in all_chapters:
        if not prev_characters: break  # no more possible successors
        if (episode_nb, chapter_nb) <= (prev_episode, prev_chapter): continue  # too soon
        # print(f'SEARCHING: next of {pretty_chapter_uid(prev_episode, prev_chapter)} searched in {pretty_chapter_uid(episode_nb, chapter_nb)}…')
        overlap = prev_characters & characters
        if overlap:  # there is an overlap !
            prev_characters -= characters
            # print(f'\tOVERLAP BETWEEN {prev_episode}/{prev_chapter} and {episode_nb}/{chapter_nb} on {"/".join(overlap)}')
            yield name, frozenset(overlap)


def pretty_list_of_chapters(all_chapters:tuple) -> [str]:
    "Maps function pretty_chapter_uid on all given chapters"
    for episode, chapter, name, characters in all_chapters:
        yield name

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
        # 'width': 4000,
        # 'height': 1000,
        'orientation': 'h',
        'valuesuffix': " personnages",
        'valueformat': '.i',
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


def sankey_chart_for_episodes(episodes:range=range(1, 17), ignore_chars:set=set(),
                              restrict_chars:set=None, merge_identicals:bool=False,
                              io_chapters:bool=True, **kwargs) -> dict:
    chapter_to_chars = associations_for_episodes(episodes, ignore_chars=ignore_chars, restrict_chars=restrict_chars)
    if merge_identicals:
        chapter_to_chars = merge_identical_chapters(chapter_to_chars)
    chapter_to_chars = tuple(chapter_to_chars)
    all_characters = set.union(*(chars for _e, _c, _n, chars in chapter_to_chars))
    # print('ALL CHARS:')
    # pprint(all_characters)

    # populate input/output chapters tuple
    if io_chapters:
        chapter_to_chars = tuple(add_io_chapters(chapter_to_chars, all_characters))

    # Build data for the sankey chart
    chart_labels = tuple(pretty_list_of_chapters(chapter_to_chars))
    chart_labels_index = {l: i for i, l in enumerate(chart_labels)}
    sources, targets, values, descs = zip(*build_links(chapter_to_chars))

    # map sources and targets to their index in the labels list
    sources = tuple(chart_labels_index[source] for source in sources)
    targets = tuple(chart_labels_index[target] for target in targets)

    # make the chart
    make_sankey_chart(chart_labels, sources, targets, values, descs, **kwargs)


if __name__ == "__main__":
    from definitions import DEFAULT_RESTRICT_CHARS, DEFAULT_IGNORE_CHARS
    # DEFAULT_RESTRICT_CHARS = None  # uncomment to get full timeline
    sankey_chart_for_episodes(range(6, 12), ignore_chars=DEFAULT_IGNORE_CHARS, restrict_chars=DEFAULT_RESTRICT_CHARS)
