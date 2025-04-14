import pytest
from pytest import MonkeyPatch
from app.utils.env import ensure_psycopg_url, coerce_bool, LazyEnvVar


def test_ensure_psycopg_url():
    # Test postgres:// conversion
    assert (
        ensure_psycopg_url("postgres://user:pass@host:5432/db")
        == "postgresql+psycopg://user:pass@host:5432/db"
    )

    # Test postgresql:// conversion
    assert (
        ensure_psycopg_url("postgresql://user:pass@host:5432/db")
        == "postgresql+psycopg://user:pass@host:5432/db"
    )

    # Test already correct format
    url = "postgresql+psycopg://user:pass@host:5432/db"
    assert ensure_psycopg_url(url) == url


def test_coerce_bool():
    # Test various truthy values
    assert coerce_bool("true") is True
    assert coerce_bool("True") is True
    assert coerce_bool("1") is True
    assert coerce_bool("yes") is True
    assert coerce_bool("Y") is True

    # Test various falsy values
    assert coerce_bool("false") is False
    assert coerce_bool("False") is False
    assert coerce_bool("0") is False
    assert coerce_bool("no") is False
    assert coerce_bool("n") is False


@pytest.fixture
def string_config():
    class Config:
        TEST_VAR = LazyEnvVar("default")

    return Config()


@pytest.fixture
def type_config():
    class Config:
        INT_VAR = LazyEnvVar(42)
        BOOL_VAR = LazyEnvVar(True)
        FLOAT_VAR = LazyEnvVar(3.14)

    return Config()


def test_basic_string_value(string_config, monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("TEST_VAR", "from_env")
    assert string_config.TEST_VAR == "from_env"


def test_type_coercion(type_config, monkeypatch: MonkeyPatch) -> None:
    # Test integer coercion
    monkeypatch.setenv("INT_VAR", "123")
    assert type_config.INT_VAR == 123

    # Test boolean coercion
    monkeypatch.setenv("BOOL_VAR", "true")
    assert type_config.BOOL_VAR is True

    # Test float coercion
    monkeypatch.setenv("FLOAT_VAR", "2.718")
    assert type_config.FLOAT_VAR == 2.718


def test_default_value(type_config, string_config) -> None:
    assert type_config.INT_VAR == 42
    assert type_config.BOOL_VAR is True
    assert type_config.FLOAT_VAR == 3.14
    assert string_config.TEST_VAR == "default"


def test_missing_required_value() -> None:
    class Config:
        REQUIRED_VAR = LazyEnvVar(None)

    config = Config()
    with pytest.raises(ValueError, match="Env var REQUIRED_VAR is not set"):
        _ = config.REQUIRED_VAR


def test_invalid_type_coercion(type_config, monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("INT_VAR", "not_an_integer")
    with pytest.raises(ValueError, match="invalid literal for int"):
        _ = type_config.INT_VAR
