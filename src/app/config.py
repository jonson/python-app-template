from app.utils.env import LazyEnvVar, PostgresDbUrl


class Config:
    # Type annotations help IDEs recognize the expected types
    DATABASE_URL: str = PostgresDbUrl()
    BUILD_TIMESTAMP: int = LazyEnvVar(0)
    DEBUG_MODE: bool = LazyEnvVar(False)


class DevelopmentConfig(Config):
    # override any defaults for local development
    pass


class TestConfig(Config):
    # override any defaults for testing
    pass
