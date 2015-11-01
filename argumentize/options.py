class Option:
    __slots__ = ['value', 'type', 'help', 'nargs', 'name']

    def __init__(self, value, name=None, help=None, nargs=1):
        self.value = value
        self.name = name
        self.help = help
        self.nargs = nargs

    def __repr__(self):
        return "<{cls}(name={name}, value={value})".format(
            value=self.value, name=self.name, cls=str(self.__class__))

    def argparse_option(self, parser):
        name = '--' + self.name
        parser.add_argument(name, type=self.type)


class OptionBool(Option):
    type = bool

    def argparse_option(self, parser):
        action = 'store_false' if self.value else 'store_true'
        name = '--no-' + self.name if self.value else '--' + self.name
        parser.add_argument(name, action=action)


class OptionInt(Option):
    type = int


class OptionStr(Option):
    type = str

