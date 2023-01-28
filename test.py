from configs import logger_init

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn


class Dashboard():
    app = FastAPI()

    @app.get("/")
    async def root():
        return HTMLResponse("Hello World")


if __name__ == "__main__":
    logger_init()
    dashboard = Dashboard()
    uvicorn.run(dashboard.app, host="0.0.0.0", port=5001, log_config=None)
