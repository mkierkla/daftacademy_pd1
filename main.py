from fastapi import FastAPI, Request
from starlette.routing import Route
from pydantic import BaseModel

app = FastAPI()

@app.get('/')
def hello_world():
	return {"message": "Hello World during the coronavirus pandemic!"}

@app.get('/method')
async def what_method(request: Request):
	used_method = request.method
	return {"method": used_method}

@app.put('/method')
async def what_method(request: Request):
	used_method = request.method
	return {"method": used_method}

@app.post('/method')
async def what_method(request: Request):
	used_method = request.method
	return {"method": used_method}

@app.get('hello/{name}')
def hello_name(name: str):
	return f"Hello {name}"
	
