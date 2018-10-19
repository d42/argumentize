class Option:
    __slots__ = ['value', 'type', 'help', 'nargs', 'name', '_arg_name']

    def __init__(self, value=None, *, required=False, name=None, help=None, arg_name=None, nargs=1, fmt=None):
        self._arg_name = arg_name
        self.value = value
        self.required = required
        self._value_set = False
        self.fmt = fmt
        self.name = name
        self.help = help
        self.nargs = nargs

    def __repr__(self):
        return "<{cls}(name={name}, value={value})".format(
            value=self.value, name=self.name, cls=str(self.__class__))

    def argparse_option(self, parser):
        parser.add_argument(self.arg_name, type=self.type, required=self.is_required, help=self.help)

    @property
    def arg_name(self):
        if self._arg_name:
            return self._arg_name
        return '--' + self.name.replace('_', '-').replace(' ', '-')

    def deserialize(self, value):
        new_val = self._deserialize(value)
        if self.fmt:
            new_val = self.fmt(new_val)
        return new_val

    def setopt(self, settings, value):
        new_value = self.deserialize(value)
        setattr(settings, self.name, new_value)
        self._value_set = True
        return new_value

    @property
    def is_required(self):
        return self.required and not self._value_set


class OptionBool(Option):
    type = bool

    def argparse_option(self, parser):
        const = False if self.value else True
        parser.add_argument(self.arg_name, action='store_const', dest=self.name, const=const, help=self.help)

    @property
    def arg_name(self):
        if self._arg_name:
            return self._arg_name
        name = self.name.replace('_', '-').replace(' ', '-')
        return '--no-' + name if self.value else '--' + name

    @staticmethod
    def _deserialize(value):
        if isinstance(value, str):
            if value.lower() == 'true':
                return True
            if value.lower() == 'false':
                return False
        return bool(value)


class OptionInt(Option):
    type = int

    @staticmethod
    def _deserialize(value): return int(value)


class OptionStr(Option):
    type = str

    @staticmethod
    def _deserialize(value): return str(value)
