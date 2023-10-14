from geyser import config

_reset = '\x1b[0m'
_bold = '\x1b[1m'
_dim = '\x1b[2m'
_green = '\x1b[32m'
_yellow = '\x1b[33m'
_red = '\x1b[31m'
_blue = '\x1b[34m'
_gray = '\x1b[90m'


def apply(s, color):
    if config.colors:
        return color + str(s) + _reset
    else:
        return str(s)


def bold(s):
    return apply(s, _bold)


def dim(s):
    return apply(s, _dim)


def success(s):
    return apply(s, _green)


def error(s):
    return apply(s, _red)


def warning(s):
    return apply(s, _yellow)


def info(s):
    return apply(s, _blue)


def debug(s):
    return apply(s, _blue + _dim)


def helper(s):
    return apply(s, _gray + _dim)
