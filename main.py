from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.routing import Route
from pydantic import BaseModel

app = FastAPI()
app.counter = 0

#zadanie1
@app.get('/')
def hello_world():
	return {"message": "Hello World during the coronavirus pandemic!"}

#zadanie2
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

#zadanie3
global patients
patients = []

class wez_pacjent(BaseModel):
	name: str
	surename: str

class daj_pacjent(BaseModel):
	id: int
	patient: wez_pacjent

@app.post('/patient', response_model=daj_pacjent)
def wyswietl_pacjenta(rq: wez_pacjent):
	#global patients
	gosciu = daj_pacjent(id=app.counter, patient=rq)
	patients.append(gosciu)
	app.counter += 1
	return gosciu

#zadanie 4

@app.get('patient/{pk}')
def znajdz_pacjetna(pk: int):
	#global patients
	if pk not in [ziomek.id for ziomek in patients]:
		return JSONResponse(status_code = 204, content ={})
	return patients[pk].patient

#wyklad
@app.get('hello/{name}')
def hello_name(name: str):
	return f"Hello {name}"
	
