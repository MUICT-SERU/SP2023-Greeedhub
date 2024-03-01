from _pytest import tmpdir
from ..workspace import Workspace

Workspace.set_root_path(tmpdir)

workspace = Workspace()


def test_workspace_without_args():
    assert workspace.name is "experiment"
