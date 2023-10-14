from contextlib import contextmanager
import os
import subprocess

from geyser.utils import color
from geyser import config
from geyser.utils.logging import log


@contextmanager
def cd(new_dir):
    previous_dir = os.getcwd()
    os.chdir(os.path.expanduser(new_dir))
    try:
        yield
    finally:
        os.chdir(previous_dir)


def get_output(cmd):
    prefix = color.helper('>>> ')
    spacing = '    '
    log.debug(cmd, prefix)
    try:
        output = ""
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        while p.poll() is None:
            out = p.stdout.readline()
            output += str(out)
            if config.debug:
                for line in out.splitlines():
                    log.debug(line, spacing)
        return str(output.strip())
    except subprocess.CalledProcessError as e:
        log.error(cmd, prefix)
        for line in e.output.splitlines():
            log.error(line, spacing)
        raise e


def call(cmd):
    try:
        get_output(cmd)
        return True
    except subprocess.CalledProcessError as e:
        return e.returncode == 0
