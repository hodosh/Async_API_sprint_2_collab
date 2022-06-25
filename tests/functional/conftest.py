from pathlib import Path
import typing as t

import pytest


def work_dir_() -> Path:
    return Path().absolute()


@pytest.fixture(scope='session')
def work_dir() -> Path:
    return work_dir_()


@pytest.fixture(scope='session')
def tmp_path_session(request, tmp_path_factory):
    from _pytest.tmpdir import _mk_tmp

    yield _mk_tmp(request, tmp_path_factory)


@pytest.fixture(scope='function')
def read_from_file():
    def _read_from_file(filepath: t.Union[str, Path]):
        with open(filepath, 'r') as f:
            return f.read()

    return _read_from_file


@pytest.fixture(scope='function')
def copy_lst_files(work_dir):
    def _copy_lst_files(files_list: t.Iterable[Path], to: Path = work_dir):
        for file in files_list:
            (to / file.name).write_text(
                (work_dir / file).read_text(encoding='utf-8'),
            )

    return _copy_lst_files
