import sys

from geyser.collect import notifications
from geyser.collect import sbt
from geyser.utils import color
from geyser import config
from geyser.core.graph import Graph
from geyser.utils.logging import log
from geyser.utils import jsonutils as json


# ignoring this warning since this method is meant to collect loads of local data
# pylint: disable=too-many-locals
def collect_dependencies():
    with log.tag('Collecting dependencies'):
        modules, dependencies, warnings = sbt.analyze()
        artifacts = set(sum(dependencies, ()))
        log.info(f'Found {len(artifacts)} dependencies')

        json.dump(modules, config.analysis_modules_file)
        json.dump(dependencies, config.analysis_dependencies_file)
        return modules, dependencies, artifacts, warnings


def build_graph(dependencies):
    with log.tag('Generating graph'):
        graph = Graph()
        for (f, t) in dependencies:
            graph.add(f, t)

        cycles = graph.find_cycles()
        if len(cycles) > 0:
            log.error(f'Found {len(cycles)} cycles in the dependencies graph, unable to continue')
            return graph, cycles
        else:
            return graph, None


def calculate_transitive_depth(graph, artifacts):
    with log.tag('Calculating transitive depth'):
        log.info(f'Calculating transitive graph for {color.bold(len(artifacts))} dependencies')

        levels = {}
        transitiveness_level = 1
        while not graph.empty():
            next_round = sorted(graph.next_round())

            with log.tag(f'Level {transitiveness_level}'):
                log.info(f'Found {len(next_round)} projects')
                for a in next_round:
                    levels[str(a)] = transitiveness_level
                    log.debug(f'  → {a}')

            transitiveness_level += 1

        json.dump(levels, config.analysis_levels_file)

        return transitiveness_level - 1


def run():
    modules, dependencies, artifacts, warnings = collect_dependencies()
    graph, cycles = build_graph(dependencies)

    if cycles:
        notifications.report_cycles(artifacts, cycles)
        sys.exit(1)
    elif warnings:
        transitive_depth = calculate_transitive_depth(graph, artifacts)
        notifications.report_warnings(artifacts, warnings, transitive_depth)
    else:
        transitive_depth = calculate_transitive_depth(graph, artifacts)
        notifications.report_success(artifacts, transitive_depth)
