from contextlib import contextmanager

from geyser import config
from geyser.utils import color


class Log:

    def __init__(self):
        self._tags = []

    @contextmanager
    def tag(self, t):
        self._tags.append(str(t))
        try:
            yield
        finally:
            self._tags.remove(str(t))

    def info(self, message, prefix=''):
        self._log('INFO ', color.info, message, prefix)

    def error(self, message, prefix=''):
        self._log('ERROR', color.error, message, prefix)

    def warn(self, message, prefix=''):
        self._log('WARN ', color.warning, message, prefix)

    def debug(self, message, prefix=''):
        if config.debug:
            self._log('DEBUG', color.debug, message, prefix)

    def _log(self, tag, level_color, message, prefix=''):
        level = level_color(tag)

        if len(self._tags) > 0:
            separator_symbol = color.helper('▹')
            separator = f' {separator_symbol} '
            tags = separator.join([level_color(t) for t in self._tags]) + separator
            print(f'{level} {tags}{prefix}{message}', flush=True)
        else:
            print(f'{level} {prefix}{message}', flush=True)


log = Log()
