import pytest

from argumentize import Argumentize
from argumentize.options import OptionInt, OptionStr, OptionBool


class Settings(Argumentize):
    ini_config_section = "foo"
    test_opt1 = OptionInt(42)
    test_opt2 = OptionStr("asdf")
    test_opt3 = OptionBool(False)


@pytest.fixture
def settings():
    s = Settings('test_name')
    return s


def test_args(settings):
    """:type settings: Settings """
    settings.from_args(['--test-opt1', '555', '--test-opt3'])
    assert settings.test_opt1 == 555
    assert settings.test_opt3 is True


def test_file(settings):
    """:type settings: Settings """

    settings.from_files('./test/testrc_ini', cfg='ini')
    assert settings.test_opt1 == 55
    assert settings.test_opt2 == "herp derp"
    assert settings.test_opt3 is True

    settings.from_files(['./test/testrc_yaml'], cfg='yaml')
    assert settings.test_opt3 is False

    settings.from_files(['./test/testrc_json'], cfg='json')
    assert settings.test_opt1 == 555
    assert settings.test_opt2 == "durka durka"
    assert settings.test_opt3 is False
