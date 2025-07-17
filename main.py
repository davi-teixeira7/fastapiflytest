from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def hello_fly():
    return 'hello from fly.io'

@app.get("/teste1")
async def hello_fly():
    return {
        "message": "hello from fly.io teste2"
    }

@app.get("/teste2")
async def hello_fly():
    return {
        "message": "i want to break free"
    }