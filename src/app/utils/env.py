import os


def ensure_psycopg_url(db_url: str):
    if db_url.startswith("postgres://") or db_url.startswith("postgresql://"):
        _, remainder = db_url.split("://", 1)
        db_url = f"postgresql+psycopg://{remainder}"

    return db_url


def coerce_bool(value: str):
    return (
        value.lower() == "true"
        or value.lower() == "1"
        or value.lower() == "yes"
        or value.lower() == "y"
    )


class LazyEnvVar:
    def __init__(self, default_value, coerce_func=None):
        self.default_value = default_value
        # Infer type from default_value only if no coerce_func is given
        self.var_type = (
            type(default_value)
            if coerce_func is None and default_value is not None
            else None
        )
        self.coerce_func = coerce_func
        self.name = None  # Set by __set_name__
        self._value = None
        self._initialized = False

    def __set_name__(self, owner, name):
        self.name = name

    def get_value(self):
        if self.name is None:
            raise TypeError("LazyEnvVar must be used as a class attribute.")

        raw_value: str | None = os.environ.get(self.name)

        # value that has been coerced, always in the correct type
        coerced_value = None
        # if raw_value is None:
        #     coerced_value = self.default_value
        # else:
        #     coerced_value = raw_value

        if raw_value is None and self.default_value is None:
            raise ValueError(
                f"Env var {self.name} is not set and has no default value."
            )
        elif raw_value is None:
            # we have a default, use it
            coerced_value = self.default_value
        else:
            # raw value is set, coerce the string to the correct type
            coerced_value = raw_value

            if self.coerce_func is not None:
                # coerce it as requested by the caller
                coerced_value = self.coerce_func(raw_value)
            elif self.var_type is not None:
                # this will blow up if the string value cannot be coerced to the correct type
                if self.var_type is bool:
                    # we're more forgiving with bool
                    coerced_value = coerce_bool(coerced_value)
                else:
                    # Use inferred type (e.g., int, float, str)
                    coerced_value = self.var_type(coerced_value)

        return coerced_value

    def __get__(self, instance, owner):
        if not self._initialized:
            self._value = self.get_value()

            self._initialized = True
        return self._value


class PostgresDbUrl(LazyEnvVar):
    def __init__(
        self,
        default_value="postgresql+psycopg://postgres:postgres@localhost:5432/postgres",
        coerce_func=ensure_psycopg_url,
    ):
        super().__init__(default_value, coerce_func=coerce_func)
