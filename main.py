import secrets

from fastapi import FastAPI, Request, Response, Depends, status, HTTPException, Cookie
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from starlette.routing import Route
from pydantic import BaseModel
from hashlib import sha256



app = FastAPI()
app.secret_key = '432A462D4A614E645267556B58703273357538782F413F4428472B4B62502553'
app.counter = 0
app.sessions = []

users = []

templates = Jinja2Templates(directory="templates")

security = HTTPBasic()

def get_current_user(response: Response, credentials: HTTPBasicCredentials = Depends(security)):
	correct_username = secrets.compare_digest(credentials.username, "trudnY")
	correct_password = secrets.compare_digest(credentials.password, "PaC13Nt")
	if not (correct_username and correct_password):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Incorrect email or password",
			headers={"WWW-Authenticate": "Basic"},
		)
	else:
		users.clear()
		users.append(credentials.username)
		session_token = sha256(bytes(f"{credentials.username}{credentials.password}{app.secret_key}", encoding = 'utf8')).hexdigest()
		app.sessions.clear()
		app.sessions.append(session_token)
		return session_token 

@app.post('/login')
def login(response: Response, cookie: str = Depends(get_current_user)):
    response.set_cookie(key = 'cookie', value = cookie)
    return RedirectResponse(url='/welcome')
    response.status_code = status.HTTP_302_FOUND
    response.headers["Location"] = '/welcome'

@app.post('/logout')
def wylogowanie(response: Response):
	if len(app.sessions)!=1:
		pass
	else:
		session_token = app.sessions[0]
		response.delete_cookie(key="session_token")
		app.sessions.clear()
		users.clear()
		print("wylogowano")
	return RedirectResponse(url='/')

#@app.post('/welcome')
@app.get('/welcome')
def powitanie(request: Request, response: Response, cookie: str = Cookie(None)):
	if cookie not in app.sessions:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Incorrect email or password",
			headers={"WWW-Authenticate": "Basic"},
		)
	return templates.TemplateResponse("item.html", {"request": request, "username": users[0]})

@app.post('/')
@app.get('/')
def hello_world():
	return {"message": "Hello World during the coronavirus pandemic!"}

@app.post('/method')
@app.get('/method')
async def what_method(request: Request):
	used_method = request.method
	return {"method": used_method}

@app.post('/method')
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


@app.post('/patient/{pk}')
@app.get('/patient/{pk}')
def znajdz_pacjetna(pk: int):
	if pk not in [ziomek.id for ziomek in patients]:
		return JSONResponse(status_code = 204, content ={})
	return patients[pk].patient

@app.post('hello/{name}')
@app.get('hello/{name}')
def hello_name(name: str):
	return f"Hello {name}"
	




	