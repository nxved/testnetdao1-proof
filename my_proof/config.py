from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Global settings configuration using environment variables"""

    DLP_ID: int = Field(default=39, description="Data Liquidity Pool ID")

    DLP_CONTRACT_ADDRESS: str = Field(
        default="0x238CA43C9aaa98bc2C5C7672dc30125c30a805db",
        description="Ethereum address of the DLP contract",
        pattern="^0x[a-fA-F0-9]{40}$",
    )

    FILE_ID: Optional[int] = Field(
        default=0, description="File ID in the Vana data registry"
    )

    OWNER_ADDRESS: Optional[str] = Field(
        default=None,
        description="Ethereum address of the data owner",
        pattern="^0x[a-fA-F0-9]{40}$",
    )

    RPC_URL: str = Field(
        default="https://rpc.moksha.vana.org",
        description="Ethereum RPC endpoint URL",
        pattern="^https?://.*$",
    )

    INPUT_DIR: str = Field(
        default="/input", description="Directory containing input files to process"
    )

    OUTPUT_DIR: str = Field(
        default="/output", description="Directory where output files will be written"
    )


    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
