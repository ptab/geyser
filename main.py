#!/usr/bin/env python3

import argparse
import re

from geyser import config
from geyser.collect import collect
from geyser.core.artifact import Artifact
from geyser.report import artifact
from geyser.report import project


def _positive(param):
    if param is None:
        return None
    elif int(param) > 0:
        return int(param)
    else:
        parser.error(f'The provided number {int(param)} must be positive (> 0)')
        return None


def _artifact(param):
    if param is None or param is False:
        return None
    else:
        match = re.search(r'(.+):(.+)', param)
        if match:
            return Artifact(match.group(1), match.group(2), False)
        else:
            parser.error(f"The provided artifact '{param}' must follow the format organization:name")
            return None


def _collect(args):
    collect.run()


def _report(args):
    config.internal_only = args.internal_only

    if args.artifact:
        artifact.report(_artifact(args.artifact), args.per_level)
    else:
        project.report(_positive(args.limit))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers()

    cmd_collect = commands.add_parser('collect')
    cmd_collect.set_defaults(func=_collect)
    cmd_collect.add_argument('-d', '--debug', help='increase the verbosity (produces more output)', action='store_true', default=config.debug)
    cmd_collect.add_argument('--no-colors', help='disable colored output', action='store_true', default=(not config.colors))

    cmd_statistics = commands.add_parser('report')
    cmd_statistics.set_defaults(func=_report)
    cmd_statistics.add_argument('-a', '--artifact', help='the artifact name (in the format organization:name)')
    cmd_statistics.add_argument('-i', '--internal-only', help='display only internal artifacts', action='store_true', default=False)
    cmd_statistics.add_argument('-l', '--limit', help='limit lists to <limit> entries', type=int)
    cmd_statistics.add_argument('-d', '--debug', help='increase the verbosity (produces more output)', action='store_true', default=config.debug)
    cmd_statistics.add_argument('--per-level', help='group dependencies and references by their transitiveness depth', action='store_true', default=False)
    cmd_statistics.add_argument('--no-colors', help='disable colored output', action='store_true', default=(not config.colors))

    arguments = parser.parse_args()

    config.debug = arguments.debug
    config.colors = not arguments.no_colors

    arguments.func(arguments)
