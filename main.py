from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def hello_fly():
    return 'hello from fly.io'

@app.get("/deploy")
async def hello_fly():
    return {
        "message": "testando deploy no fly.io"
    }

@app.get("/healthstatus")
async def hello_fly():
    return {
        "status: healthy"
    }
    
