from argparse import ArgumentParser, HelpFormatter
from functools import partial

from tool import create, thumb, cast, normalize, menu, youtube


class _HelpFormatter(HelpFormatter):
    def _format_action_invocation(self, action):
        if not action.option_strings or action.nargs == 0:
            return super()._format_action_invocation(action)
        default = self._get_default_metavar_for_optional(action)
        args_string = self._format_args(action, default)
        return ", ".join(action.option_strings) + " " + args_string


def _create_parsers():
    parser = ArgumentParser(prog="Avalon Xml Tools", description="Version 1.0.2", formatter_class=_HelpFormatter)
    subparsers = parser.add_subparsers(dest="command")

    subparsers_factories = [create.create_subparser,
                            thumb.create_subparser,
                            cast.create_subparser,
                            normalize.create_subparser,
                            youtube.create_subparser]
    funcs = {}
    for factory in subparsers_factories:
        command, func = factory(subparsers)
        funcs[command] = func
    return parser, funcs


def main():
    parser, funcs = _create_parsers()
    args = parser.parse_args()
    if args.command in funcs:
        funcs[args.command](args)
    else:
        items = [menu.MenuItem(key, partial(value, None)) for key, value in funcs.items()]
        menu.Menu(items).show()


if __name__ == "__main__":
    main()
