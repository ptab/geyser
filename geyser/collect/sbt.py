import os
import re

from geyser import config
from geyser.core.artifact import Artifact
from geyser.utils.cmd import cd
from geyser.utils.cmd import get_output
from geyser.utils.logging import log


def analyze():
    log.info("Generating dot files...")
    with cd(config.repository_path):
        if os.path.exists('build.sbt'):
            output = get_output('sbt --batch --no-colors projectID "Compile / dependencyDot" "Test / dependencyDot"').splitlines()

            modules, warnings = _extract_modules(output)

            dependencies = set()
            for file in _extract_dotfile_locations(output):
                deps, _warnings = _process_dependencies(file, modules)
                dependencies.update(deps)
                warnings += _warnings

            return modules, dependencies, warnings
        else:
            log.error(f'No build.sbt file found in {config.repository_path}, have you mounted your volumes correctly?')
            raise RuntimeError('No build.sbt file found')


def _extract_modules(raw_output):
    def _artifact(s):
        match = re.search(rf'(.+?):(.+?):.+', s)
        if match:
            return Artifact(organization=match.group(1),
                            name=match.group(2),
                            internal=True)
        else:
            raise ValueError(f'Unable to parse {s}')

    modules = set()
    warnings = []
    for i, line in enumerate(raw_output):
        if line.endswith('/ projectID'):
            to_parse = raw_output[i + 1]
            match = re.search(rf'\[info\]\s+(.+)', to_parse)
            if match:
                modules.add(_artifact(match.group(1)))
            else:
                log.warn(f'Unable to parse project line: {to_parse}')
                warnings.append(to_parse)
                raise ValueError(f'Unable to parse project line: {to_parse}')

    return modules, warnings


def _extract_dotfile_locations(raw_output):
    try:
        output = [line for line in raw_output if 'Wrote dependency graph to' in line]
        files = set()
        for line in output:
            m = re.search(rf"\[info\]\s+Wrote dependency graph to '({config.repository_path}/.+/target/dependencies-.+.dot)'", line)
            if m:
                files.add(m.group(1))
            elif f"Wrote dependency graph to '{config.repository_path}/target/dependencies-" in line:
                # ignore the file generated for the root project
                continue
            else:
                raise ValueError(f'Unable to parse filename from line: {line}')
        return files

    except (RuntimeError, Exception) as e:
        log.error(f'Unparseable output: {raw_output}')
        raise RuntimeError(f'Unable to determine modules: {e}')


def _process_dependencies(file, modules):
    def parse_filename(path):
        m = re.search(rf'{config.repository_path}/(.+)/target/dependencies-(.+).dot', path)
        if m:
            return m.group(1), m.group(2)
        else:
            raise ValueError(f'Unable to parse filename: {path}')

    def _artifact(s, internal_organization):
        match = re.search(rf'"(.+?):(.+?)(?:_{config.scala_version})?:.+"', s)
        if match:
            organization = match.group(1)
            name = match.group(2)
            internal = organization in internal_organizations
            return Artifact(organization, name, internal)
        else:
            raise ValueError(f'Unable to parse {s}')

    if os.path.exists(file):
        try:
            internal_organizations = [m.organization for m in modules]
            project, scope = parse_filename(file)
            log.info(f'Parsing {scope}-scoped dependencies from {project}')
            deps = set()
            warnings = []
            with open(file, 'r') as f:
                for line in f:
                    if ' -> ' in line and 'Evicted By' not in line:
                        try:
                            f, t, *_ = line.strip().split(' -> ')
                            dep_from = _artifact(f, internal_organizations)
                            dep_to = _artifact(t, internal_organizations)
                            deps.add((dep_from, dep_to))
                            log.debug(f'{dep_from} → {dep_to}')
                        except (RuntimeError, Exception) as e:
                            log.warn(f'Unparseable dependency, will skip line: {e}')
                            log.warn(f'Full line for investigation: {line}')
                            warnings.append(project)
            return deps, warnings
        except RuntimeError:
            log.error(f'Unable to read file {file}')
            return set(), [file]
    else:
        log.error(f'Unable to read file {file}')
        return set(), [file]
