"""CLI wrapper around the build_sankey module.

"""

import argparse
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
    # flags
    parser.add_argument('--explicit-numbering', '-e', action='store_true', default=False,
                        help="episodes parameter is understood as a list of episodes to consider instead of a range")
    parser.add_argument('--black-theme', '-b', action='store_true', default=False,
                        help="Use a black theme for the final chart")
    return parser.parse_args()


CHARACTER_MAP = {
    'zarakai': 'zarakaï',
    'énoriel': 'enoriel',
}


if __name__ == "__main__":
    args = parse_cli()

    if args.explicit_numbering:
        episodes = tuple(args.episodes)
    else:
        episodes = range(*args.episodes)
    ignore = set(map(str.upper, (CHARACTER_MAP.get(c, c) for c in args.ignore)))
    restrict = set(map(str.upper, (CHARACTER_MAP.get(c, c) for c in args.restrict_to)))
    if len(ignore) == 1 and next(iter(ignore)) == 'DEFAULT':
        ignore = build_sankey.DEFAULT_IGNORE_CHARS
    if len(restrict) == 1 and next(iter(restrict)) == 'DEFAULT':
        restrict = build_sankey.DEFAULT_RESTRICT_CHARS
    title = args.title.strip()

    print('EPISODES:', tuple(episodes))
    print('  IGNORE:', ', '.join(ignore))
    print('RESTRICT:', ', '.join(restrict))
    # exit()

    build_sankey.sankey_chart_for_episodes(episodes, ignore, restrict, title=title, black_theme=args.black_theme)
