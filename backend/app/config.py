from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///data/donteatcancer.db"
    deepseek_api_key: str = ""
    anthropic_api_key: str = ""
    backend_cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:3456"]
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    # API fetcher keys
    pubmed_api_key: str = ""       # Optional — increases rate limit to 10 req/s
    pubmed_email: str = ""         # Required by NCBI policy
    openalex_api_key: str = ""     # Required as of Feb 2026
    scopus_api_key: str = ""       # Required
    scopus_insttoken: str = ""     # Optional institutional token

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
