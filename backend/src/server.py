import os

import uvicorn

from config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.app:get_skim_app",
        factory=True,
        host=settings.HOST,
        port=int(os.environ.get("PORT", settings.PORT)),
        reload=settings.RELOAD,
        access_log=False,
        log_config=None,
    )
