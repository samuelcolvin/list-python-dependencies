import os
import random
import re
import tomllib
from pathlib import Path

import requests
from packaging.requirements import Requirement

__version__ = '0.0.1'
__all__ = ('list_dependencies',)


def list_dependencies():
    max_cases = int(os.getenv('INPUT_MAX_CASES', 0)) or None
    path = Path(os.getenv('INPUT_PATH', '.')).expanduser().resolve()
    print(f'list-dependencies __version__={__version__!r} path={path!r} max_cases={max_cases}')
    deps = load_deps(path)
    valid_versions = get_valid_versions(deps)
    cases = get_test_cases(valid_versions, max_cases=8)
    for case in cases:
        print(' '.join(f'{name}=={version}' for name, version in case))


def load_deps(path: Path) -> list[Requirement]:
    py_pyroject = path / 'pyproject.toml'
    if py_pyroject.exists():
        with py_pyroject.open('rb') as f:
            pyproject = tomllib.load(f)
        deps = [Requirement(dep) for dep in pyproject['project']['dependencies']]
        option_deps = pyproject['project'].get('optional-dependencies')
        if option_deps:
            for value in option_deps.values():
                deps.extend([Requirement(dep) for dep in value])
        return deps

    setup_py = path / 'setup.py'
    if setup_py.exists():
        setup = setup_py.read_text()
        m = re.search(r'install_requires=(\[.+?])', setup, flags=re.S)
        if not m:
            raise RuntimeError('Could not find `install_requires` in setup.py')
        install_requires = eval(m.group(1))
        deps = [Requirement(dep) for dep in install_requires]
        m = re.search(r'extras_require=(\{.+?})', setup, flags=re.S)
        if m:
            for extra_deps in eval(m.group(1)).values():
                deps.extend(Requirement(dep) for dep in extra_deps)
        return deps

    raise RuntimeError(f'No {py_pyroject.name} or {setup_py.name} found in {path}')


def get_valid_versions(deps: list[Requirement]) -> dict[str, list[str]]:
    session = requests.Session()
    valid_versions: dict[str, list[str]] = {}
    for dep in deps:
        resp = session.get(f'https://pypi.org/pypi/{dep.name}/json')
        resp.raise_for_status()
        versions = resp.json()['releases'].keys()
        compat_versions = [v for v in versions if v in dep.specifier]
        if not compat_versions:
            raise RuntimeError(f'No compatible versions found for {dep.name}')
        valid_versions[dep.name] = compat_versions
    return valid_versions


def get_test_cases(valid_versions: dict[str, list[str]], max_cases: int | None = None) -> list[list[tuple[str, str]]]:
    min_versions_case = [(name, versions[0]) for name, versions in valid_versions.items()]
    cases = []

    for name, versions in valid_versions.items():
        for v in versions[1:]:
            case = [(n, v if n == name else min_v) for n, min_v in min_versions_case]
            cases.append(case)

    if max_cases and len(cases) >= max_cases:
        print(f'{len(cases) + 1} cases generated, truncating to {max_cases}')
        random.shuffle(cases)
        trunc_cases = cases[: max_cases - 1]
        return [min_versions_case] + sorted(trunc_cases)
    else:
        print(f'{len(cases) + 1} cases generated')
        return [min_versions_case] + cases
