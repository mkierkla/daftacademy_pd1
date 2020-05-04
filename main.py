import secrets

import aiosqlite
import sqlite3

from fastapi import FastAPI, Request, Response, Depends, status, HTTPException, Cookie, Query
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

#-----------------------funkcje---------------------------------

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

def check_if_logged(cookie: str):
		if cookie not in app.sessions:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Incorrect email or password",
			)

#-----------------------endpointy---------------------------------

@app.post('/login')
def login(response: Response, cookie: str = Depends(get_current_user)):
    response.set_cookie(key = 'cookie', value = cookie)
    response.status_code = status.HTTP_302_FOUND
    response.headers["Location"] = '/welcome'
    #return RedirectResponse(url='/welcome')


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
	check_if_logged(cookie)
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


#--------------------SQL------------------------------------------

@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect('chinook/chinook.db')


@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()


@app.get('/tracks/')
async def read_tracks(page: int = Query(0), per_page: int = Query(10)): 
	app.db_connection.row_factory = sqlite3.Row
	data = app.db_connection.execute(
		"SELECT * FROM tracks ORDER BY TrackId").fetchall()
	current_tracks = data[per_page*page:per_page*(page+1)]
	return current_tracks

@app.get('/tracks/composers')
async def read_composers(composer_name: str = Query(None)):
	app.db_connection.row_factory = sqlite3.Row
	data = app.db_connection.execute(
		"SELECT Name FROM tracks WHERE Composer= :composer_name ORDER BY Name",
		{'composer_name': composer_name}).fetchall()

	traki = []
	for elem in data:
		traki.append(elem["Name"])

	if len(data)==0:
		raise HTTPException(
			status_code=404,
			detail= {"error": "Composer not in database"}
		)

	return traki

class album_info(BaseModel):
	title: str
	artist_id: int = 1

class albums_entry:
	AlbumId: int
	Title: str
	ArtistId: str

class customer_info(BaseModel):
	company: str = None
	address: str = None
	city: str = None
	state: str = None
	country: str = None
	postalcode: str = None
	fax: str = None

@app.get('/albums/{album_id}')
async def read_albums(album_id:int):
	app.db_connection.row_factory = sqlite3.Row
	data = app.db_connection.execute("SELECT * FROM albums WHERE AlbumId=:album_id", {"album_id": album_id}).fetchall()
	return data[0]

@app.post('/albums') #, response_model=albums_entry
async def create_album(album_rq: album_info):

	app.db_connection.row_factory = sqlite3.Row

	check_artist = app.db_connection.execute("SELECT Name FROM artists WHERE ArtistId=:artistId", 
		{"artistId": album_rq.artist_id}).fetchone()

	if check_artist!=None:

		inserted_data = app.db_connection.execute("INSERT INTO albums (Title, ArtistId) VALUES (:title, :artistId)",
			{"title": album_rq.title, "artistId": album_rq.artist_id})
		app.db_connection.commit()
		

		new_album_id=inserted_data.lastrowid
		app.db_connection.row_factory = sqlite3.Row
		get_data = app.db_connection.execute("SELECT * FROM albums WHERE AlbumId=:new_album_id", {"new_album_id": new_album_id}).fetchall()

		temp = albums_entry()
		for elem in get_data:
			temp.AlbumId = elem["AlbumId"]
			temp.Title = elem["Title"]
			temp.ArtistId = elem["ArtistId"]

		if get_data!=None:
			return JSONResponse(
				status_code=201,
				content = {"AlbumId": temp.AlbumId, "Title": temp.Title, "ArtistId": temp.ArtistId}
			)	
	else:
		raise HTTPException(
			status_code=404,
			detail= {"error": "ArtistId not in database"}
		)

@app.put('/customers/{customer_id}')
async def update_customer(customer_id:int, updated_rq: customer_info):
	app.db_connection.row_factory = sqlite3.Row

	check_customer = app.db_connection.execute("SELECT FirstName FROM customers WHERE CustomerId=:customer_id", {"customer_id": customer_id}).fetchone()
	if check_customer!=None:
		for key, value in updated_rq.__dict__.items():
			#print(key.capitalize(), value)
			if key == 'postalcode':
				temp_key = 'PostalCode'
			else:
				temp_key = key.capitalize()
			sql_text = "UPDATE customers SET " + str(temp_key) + " = '" + str(value) + "' WHERE CustomerID = " + str(customer_id)
			print(sql_text)
			update = app.db_connection.execute(sql_text)
			app.db_connection.commit()
		data = app.db_connection.execute("SELECT * FROM customers WHERE CustomerId=:customer_id", {"customer_id": customer_id}).fetchone()
		if data==None:
			raise HTTPException(
				status_code=404,
				detail= {"error": "CustomerId not in database"}
			)
		else:
			return data
	else:
		raise HTTPException(
			status_code=404,
			detail= {"error": "CustomerId not in database"}
		)

#----------------------pacjenci-----------------------------------

global patients
patients = []

class wez_pacjent(BaseModel):
	name: str
	surname: str

class daj_pacjent(BaseModel):
	id: int
	patient: wez_pacjent


@app.post('/patient', response_model=daj_pacjent) #
def stworz_pacjenta(rq: wez_pacjent, cookie: str = Cookie(None)):
	check_if_logged(cookie)
	index = app.counter
	gosciu = daj_pacjent(id=app.counter, patient=rq)
	patients.append(gosciu)
	app.counter += 1
	print(len(patients))
	return RedirectResponse(url='/patient/%i' % index)


@app.get('/patient')
def poka_pacjentow(cookie: str = Cookie(None)): #request: Request, response: Response,
	check_if_logged(cookie)
	if len(patients)==0:
		raise HTTPException(status_code=401, detail = "brak pacjentow")

	dict_of_patients = {}
	count = 0
	for i in patients:
		dict_of_patients["id_%s" % count] = i.patient
		count += 1

	return dict_of_patients

@app.post('/patient/{pk}')
@app.get('/patient/{pk}')
def znajdz_pacjetna(pk: int):
	if len(patients)==0:
		raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
	if pk not in [ziomek.id for ziomek in patients]:
		return JSONResponse(status_code = 204, content ={})
	return patients[pk].patient


@app.delete('/patient/{pk}')
def usun_pacjenta(pk: int, cookie: str = Cookie(None)):
	check_if_logged(cookie)
	if len(patients)==0:
		raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
	if pk in [ziomek.id for ziomek in patients]:
		patients.pop(pk)
		raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)



@app.post('hello/{name}')
@app.get('hello/{name}')
def hello_name(name: str):
	return f"Hello {name}"
	

#status_code=status.HTTP_401_UNAUTHORIZED,

	