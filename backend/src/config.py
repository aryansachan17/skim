from pathlib import Path

from dynaconf import Dynaconf, Validator

settings = Dynaconf(
    root_path=Path(__file__).resolve().parent.parent,
    settings_files=["settings.toml"],
    environments=True,
    env_switcher="SKIM_ENV",
    envvar_prefix="SKIM",
    load_dotenv=True,
    validators=[
        Validator("MONGO_URI", "MONGO_DB", "REDIS_URL", must_exist=True),
        Validator("EXPOSE_ERROR_DETAILS", "GRAPHQL_IDE", eq=False, env=["staging", "production"]),
    ],
)
