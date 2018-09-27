"""CLI wrapper around the build_sankey module.

"""


import argparse

import definitions
import build_sankey


def parse_cli():
    parser = argparse.ArgumentParser(description=__doc__)
    # main args
    parser.add_argument('episodes', type=int, nargs='+', metavar='EPISODE',
                        help="Episodes to consider, like '2 15' to get episode 2 to 15")
    # options
    parser.add_argument('--ignore', '-i', nargs='+', metavar='CHARACTER',
                        default=(), help="Characters name to ignore")
    parser.add_argument('--restrict-to', '-r', nargs='+', metavar='CHARACTER',
                        default=(), help="Only use given character names, ignore the other. -i will have no effect")
    parser.add_argument('--title', '-t', type=str,
                        default=build_sankey.DEFAULT_TITLE,
                        help="Title given to the final chart")
    parser.add_argument('--output-file', '-o', default=None,
                        help="File to write with output HTML data. If None, outputs in stdout.")
    # flags
    parser.add_argument('--explicit-numbering', '-e', action='store_true', default=False,
                        help="episodes parameter is understood as a list of episodes to consider instead of a range")
    parser.add_argument('--black-theme', '-b', action='store_true', default=False,
                        help="Use a black theme for the final chart")
    parser.add_argument('--merge-identicals', '-m', action='store_true', default=False,
                        help="Merge chapters involving exactly the same characters")
    parser.add_argument('--io-chapters', '-io', action='store_true', default=False,
                        help="Add phony chapters introducing and finishing all characters")
    return parser.parse_args()


CHARACTER_MAP = {
    'zarakai': 'zarakaï',
    'énoriel': 'enoriel',
    'dragonne': 'alia',
}


if __name__ == "__main__":
    args = parse_cli()

    if args.explicit_numbering:
        episodes = tuple(args.episodes)
    else:
        if len(args.episodes) == 2:
            start, end = args.episodes
            step = 1
        elif len(args.episodes) == 3:
            start, end, step = args.episodes
        else:
            raise ValueError('episodes parameter needs 2 or 3 values')
        episodes = range(start, end+1, step)
    ignore = set(map(str.upper, (CHARACTER_MAP.get(c, c) for c in args.ignore)))
    restrict = set(map(str.upper, (CHARACTER_MAP.get(c, c) for c in args.restrict_to)))
    if 'DEFAULT' in ignore:
        ignore.remove('DEFAULT')
        ignore |= definitions.DEFAULT_IGNORE_CHARS
    if 'NONE' in ignore:
        ignore = set()
    if 'DEFAULT' in restrict:
        restrict.remove('DEFAULT')
        restrict |= definitions.DEFAULT_RESTRICT_CHARS
    if 'NONE' in restrict:
        restrict = set()
    for name in set(ignore):
        print('NAME:', name)
        if name.startswith(('—', '^')): ignore -= {name, name.lstrip('—^')}
    for name in set(restrict):
        if name.startswith(('—', '^')): restrict -= {name, name.lstrip('—^')}
    title = args.title.strip()

    print('EPISODES:', tuple(episodes))
    print('  IGNORE:', ', '.join(ignore))
    print('RESTRICT:', ', '.join(restrict))

    html = build_sankey.sankey_chart_for_episodes(
        episodes, ignore, restrict,
        title=title,
        black_theme=args.black_theme,
        merge_identicals=args.merge_identicals,
        io_chapters=args.io_chapters,
    )
    if args.output_file:
        with open(args.output_file, 'w') as fd:
            fd.write(html)
    else:  # write it in stdout
        print(html)
