def main() -> None:
    import uvicorn

    from backend.config.env_config import settings

    uvicorn.run("backend.main:app", host=settings.app_host, port=settings.app_port)
