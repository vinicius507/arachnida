from pydantic import Field, HttpUrl
from pydantic_settings import (
    BaseSettings,
    CliPositionalArg,
    CliSettingsSource,
    PydanticBaseSettingsSource,
)


class SpiderSettings(BaseSettings):
    """Extracts images from a given URL."""

    url: CliPositionalArg[HttpUrl] = Field(description="The URL to extract images from")

    # NOTE: This is a workaraound to avoid Pyright error when instantiating the class
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (CliSettingsSource(settings_cls, cli_parse_args=True),)
