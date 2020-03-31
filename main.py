from fastapi import FastAPI, Request

app = FastAPI()

@app.get('/')
def hello_world():
	return {"message": "Hello World during the coronavirus pandemic!"}

@app.get('/method')
def what_method(request: Request):
	used_method = request.method
	return {"method": used_method}

@app.get('hello/{name}')
def hello_name(name: str):
	return f"Hello {name}"
	
