import uvicorn

from infrastructure.api import create_api

api = create_api()

if __name__ == "__main__":
    uvicorn.run("main_api:api", host="0.0.0.0", port=8000, reload=True)