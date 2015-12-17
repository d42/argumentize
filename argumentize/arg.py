from .options import Option

import os
import sys
import json
import logging
from enum import Enum

import inspect
import argparse
from six.moves.configparser import ConfigParser

logger = logging.getLogger('argumentize')

import yaml


XDG_CONFIG_DIR = os.environ.get('XDG_CONFIG_DIR', '.config')
CURRENT_DIR = os.path.abspath(os.path.dirname(sys.argv[0]))

DEFAULT_PATHS = tuple([
    os.path.expanduser('~/.{namerc}'),
    os.path.expanduser('~/{cfg}/{{namerc}}'.format(cfg=XDG_CONFIG_DIR)),
    os.path.join(CURRENT_DIR, '{namerc}')
])


class ConfigTypes(Enum):
    ini = 'ini'
    json = 'json'
    yaml = 'yaml'


class Argumentize:
    ini_config_section = None
    namerc = None

    def __init__(self, name):
        self.name = name
        self._options = OptionReader(self.__class__).options
        self.from_dict({o.name: o.value for o in self._options.values()})

    def from_args(self, args, verbose=False):
        parser = self._gen_argparse()
        options = parser.parse_args(args)
        self.from_dict({k: v for k, v in options._get_kwargs()
                        if v is not None}, verbose)

    def _gen_argparse(self):
        parser = argparse.ArgumentParser()
        for option in self._options.values():
            option.argparse_option(parser)
        return parser

    def from_files(self, paths=DEFAULT_PATHS, cfg=ConfigTypes.ini, verbose=False):
        if isinstance(paths, str):
            paths = [paths]
        if isinstance(cfg, str):
            cfg = ConfigTypes[cfg]

        paths = self._format_paths(paths)
        for p in paths:
            if verbose:
                logger.info("checking %s", p)
            if os.path.exists(p) and os.path.isfile(p):
                key_value = self.read_file(p, cfg=cfg)
                self.from_dict(key_value, verbose)

    def from_dict(self, options_dict, verbose=False):
        for k, v in options_dict.items():
            option = self._options.get(k, None)
            if option is None:
                continue
            if verbose:
                logger.info("set %s to %s", k, v)

            new_v = option.deserialize(v)
            setattr(self, k, new_v)

    def read_file(self, p, cfg):
        if cfg == ConfigTypes.ini:
            return self._read_ini(p)
        elif cfg == ConfigTypes.yaml:
            return self._read_yaml(p)
        elif cfg == ConfigTypes.json:
            return self._read_json(p)
        else:
            raise ValueError("unknown type: %s" % cfg)

    def _read_ini(self, path):
        if self.ini_config_section is None:
            raise ValueError()
        parser = ConfigParser()
        parser.read(path)
        return {k:v for k,v in parser.items(self.ini_config_section)}

    def _read_yaml(self, path):
        with open(path) as file:
            content = yaml.load(file.read())
        return content

    def _read_json(self, path):
        with open(path) as file:
            content = json.loads(file.read())
        return content

    def _format_paths(self, paths):
        namerc = self.namerc or self.name + 'rc'
        return [p.format(name=self.name, namerc=self.name+'rc')
                for p in paths]


class OptionReader:
    def __init__(self, inspected_class, base_class=Argumentize):
        self.cl = inspected_class
        self.base_class = base_class

    @property
    def options(self):
        options = dict()
        for cl in self._inheriting_classes:
            class_options = self.read_class_options(cl)
            for o in class_options:
                if o.name in options:
                    continue
                options[o.name] = o

        return options

    @staticmethod
    def read_class_options(cl):
        for name in dir(cl):
            attr = getattr(cl, name)
            if isinstance(attr, Option):
                attr.name = name
                yield attr

    @property
    def _inheriting_classes(self):
        for c in inspect.getmro(self.cl):
            if c is self.base_class:
                return
            yield c
