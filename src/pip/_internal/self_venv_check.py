import sys
import logging
import shutil

from pathlib import Path
from dataclasses import dataclass

from pip._vendor.rich.console import Group
from pip._vendor.rich.markup import escape
from pip._vendor.rich.text import Text


logger = logging.getLogger(__name__)


@dataclass
class VenvPrompt:
    local: str
    system: str

    def __rich__(self) -> Group:
        notice = "[bold][[reset][blue]notice[reset][bold]][reset]"

        return Group(
            Text(),
            Text.from_markup(
                f"{notice} This pip might not be using the Python interpreter you expect. "
                f"It is using [yellow]{self.local}[reset] but [yellow]{self.system}[reset] is "
                f"the one on your $PATH."
            ),
        )


def pip_self_venv_check():
    # Disable this check if we are in a virtual environment.
    if sys.base_prefix != sys.prefix:
        return False

    # Disable this check if Python was explicitly selected `python -m pip`.
    exec_path = Path(sys.executable)
    proc_path = Path("/proc/self/cmdline")

    if proc_path.exists():
        # This is the fully resolved path
        command_path = Path(proc_path.read_text().split("\x00")[0])

    # Otherwise pip was executed as either `pip` or `pip3`, lets see if our
    # executable is the same as the one on PATH.
    on_path = Path(shutil.which("python3"))

    # If there's no Python executable on PATH we can't say anything that makes
    # sense.
    if not on_path:
        return False

    # And when the on_path Python is the same as our executable we're already
    # using the correct one.
    if exec_path == on_path:
        return False

    logger.info("[present-rich] %s", VenvPrompt(local=sys.executable, system=on_path))
