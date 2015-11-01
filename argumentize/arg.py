from .options import Option

import os
import sys

import inspect
import argparse
from six.moves.configparser import ConfigParser

import yaml


XDG_CONFIG_DIR = os.environ.get('XDG_CONFIG_DIR', '.config')
CURRENT_DIR = os.path.abspath(os.path.dirname(sys.argv[0]))

DEFAULT_PATHS = [
    os.path.expanduser('~/.{namerc}'),
    os.path.expanduser('~/{cfg}/{{namerc}}'.format(cfg=XDG_CONFIG_DIR)),
    os.path.join(CURRENT_DIR, '{namerc}')
]

class Argumentize:

    def __init__(self, name):
        self.name = name
        self._options = OptionReader(self.__class__).options
        for o in self._options:
            setattr(self, o.name, o.value)

    def from_args(self, args):
        parser = self._gen_argparse()
        options = parser.parse_args(args)
        for option, value in options._get_kwargs():
            if value is None:
                continue
            setattr(self, option, value)

    def _gen_argparse(self):
        parser = argparse.ArgumentParser()
        for option in self._options:
            option.argparse_option(parser)
        return parser

    def from_files(self, paths=DEFAULT_PATHS, type='ini'):
        paths = self._format_paths(paths)
        for p in paths:
            if os.path.exists(p) and os.path.isfile(p):
                self.read_file(p, type=type)

    def read_file(self, p, type):
        if type == 'ini':
            return self._read_ini(p)
        if type == 'yaml':
            return self._read_yaml(p)

    @staticmethod
    def _read_ini(path):
        parser = ConfigParser()
        parser.read(path)
        import ipdb; ipdb.set_trace()
        content = ConfigParser.read(path)

    def _format_paths(self, paths):
        return [p.format(name=self.name, namerc=self.name+'rc')
                for p in paths]



class OptionReader:
    def __init__(self, cls, base_class=Argumentize):
        self.cls = cls
        self.base_class = base_class

    @property
    def options(self):
        options = dict()
        for cls in self._inheriting_classes:
            class_options = self.read_class_options(cls)
            for o in class_options:
                if o.name in options:
                    continue
                options[o.name] = o

        return options.values()

    def read_class_options(self, cls):
        for name in dir(cls):
            attr = getattr(cls, name)
            if isinstance(attr, Option):
                attr.name = name
                yield attr

    @property
    def _inheriting_classes(self):
        for c in inspect.getmro(self.cls):
            if c is self.base_class:
                return
            yield c
