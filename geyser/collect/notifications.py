from geyser import config
from geyser.utils import color
from geyser.utils import symbol


def report_success(artifacts, transitive_depth):
    print()

    print(f'{symbol.success} geyser finished successfully, all good! 👌')
    print(f'{symbol.success} Analyzed {color.bold(len(artifacts))} dependencies')
    print(f'→ Detected {color.bold(transitive_depth)} levels of transitive dependencies')
    print()


def report_warnings(artifacts, warnings, transitive_depth):
    print()

    print(f'{symbol.warning} geyser finished successfully, but there are still some warnings to deal with 😒')
    print(f'{symbol.success} Analyzed {color.bold(len(artifacts))} dependencies')
    print(f'→ Detected {color.bold(transitive_depth)} levels of transitive dependencies')
    print()

    print(f'{symbol.warning} ' + color.warning(f'{len(warnings)} processed with warnings'))
    for r in sorted(warnings):
        print(f'  {symbol.warning} {r}')


def report_cycles(artifacts, cycles):
    print()
    print(f'{symbol.cycle} geyser did not finish successfully, found cycle(s) in our dependencies graph 😱')
    print(f'{symbol.success} Analyzed {color.bold(len(artifacts))} dependencies')
    print()

    print(f'{symbol.cycle} ' + color.error(f'{len(cycles)} cycle(s) found'))
    for cycle in cycles:
        cycle_text = color.error(' → ').join([str(c) for c in cycle])
        print(f'  {symbol.cycle} {cycle_text}')
