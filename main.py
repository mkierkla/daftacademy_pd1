import secrets

from fastapi import FastAPI, Request, Response, Depends, status, HTTPException, Cookie
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.routing import Route
from pydantic import BaseModel
from hashlib import sha256



app = FastAPI()
app.secret_key = '432A462D4A614E645267556B58703273357538782F413F4428472B4B62502553'
app.counter = 0

security = HTTPBasic()


@app.post('/login')
def logowanie(response: Response, credentials: HTTPBasicCredentials = Depends(security)):
	#sprawdzam czy dobre passy
	correct_username = secrets.compare_digest(credentials.username, "gosc")
	correct_password = secrets.compare_digest(credentials.password, "pass")
	#komunikat jak zle
	if not (correct_username and correct_password):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Incorrect email or password",
			headers={"WWW-Authenticate": "Basic"},
		)
	#to bedzie sie dzialo jak dobre passy
	else: 
		session_token = sha256(bytes(f"{credentials.username}{credentials.password}{app.secret_key}",encoding='utf8')).hexdigest()
		response.set_cookie(key="session_token", value=session_token)
		return RedirectResponse(url='/welcome') 

@app.post('/welcome')
@app.get('/welcome')
def powitanie():
	return {"message": "jakis powitalny tekst"}

#@app.post('welcome')
@app.get('/')
def hello_world():
	return {"message": "Hello World during the coronavirus pandemic!"}

#@app.post('welcome')
@app.get('/method')
async def what_method(request: Request):
	used_method = request.method
	return {"method": used_method}

#@app.post('welcome')
@app.put('/method')
async def what_method(request: Request):
	used_method = request.method
	return {"method": used_method}

@app.post('/method')
async def what_method(request: Request):
	used_method = request.method
	return {"method": used_method}


global patients
patients = []

class wez_pacjent(BaseModel):
	name: str
	surename: str

class daj_pacjent(BaseModel):
	id: int
	patient: wez_pacjent

#@app.post('welcome')
@app.post('/patient', response_model=daj_pacjent)
def wyswietl_pacjenta(rq: wez_pacjent):
	gosciu = daj_pacjent(id=app.counter, patient=rq)
	patients.append(gosciu)
	app.counter += 1
	return gosciu


#@app.post('welcome')
@app.get('/patient/{pk}')
def znajdz_pacjetna(pk: int):
	if pk not in [ziomek.id for ziomek in patients]:
		return JSONResponse(status_code = 204, content ={})
	return patients[pk].patient

#@app.post('welcome')
@app.get('hello/{name}')
def hello_name(name: str):
	return f"Hello {name}"
	




	