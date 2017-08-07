class Option:
    __slots__ = ['value', 'type', 'help', 'nargs', 'name', '_arg_name']

    def __init__(self, value, name=None, help=None, arg_name=None, nargs=1):
        self._arg_name = arg_name
        self.value = value
        self.name = name
        self.help = help
        self.nargs = nargs

    def __repr__(self):
        return "<{cls}(name={name}, value={value})".format(
            value=self.value, name=self.name, cls=str(self.__class__))

    def argparse_option(self, parser):
        parser.add_argument(self.arg_name, type=self.type)

    @property
    def arg_name(self):
        if self._arg_name:
            return self._arg_name
        return '--' + self.name.replace('_', '-').replace(' ', '-')


class OptionBool(Option):
    type = bool

    def argparse_option(self, parser):
        action = 'store_false' if self.value else 'store_true'
        parser.add_argument(self.arg_name, action=action, dest=self.name)

    @property
    def arg_name(self):
        if self._arg_name:
            return self._arg_name
        name = self.name.replace('_', '-').replace(' ', '-')
        return '--no-' + name if self.value else '--' + name

    @staticmethod
    def deserialize(value):
        if isinstance(value, str):
            if value.lower() == 'true':
                return True
            if value.lower() == 'false':
                return False
        return bool(value)


class OptionInt(Option):
    type = int

    @staticmethod
    def deserialize(value): return int(value)


class OptionStr(Option):
    type = str

    @staticmethod
    def deserialize(value): return str(value)
