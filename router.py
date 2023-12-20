from fastapi import APIRouter, Depends
from schema import RequestSchema, ResponseSchema, TokenResponse
from sqlalchemy.orm import Session
from config import get_db
from passlib.context import CryptContext
from repository import JWTRepo, JWTBearer, UsersRepo
from model import Users

router = APIRouter()


pwd_context = CryptContext(schemes=['bcrypt'], deprecated = "auto")

@router.post('/singup')
async def signup(request: RequestSchema, db: Session = Depends(get_db)):
    try:
        _user = Users(username = request.parameter.data['username'],
                      email = request.parameter.data['email'],
                      phone_number = request.parameter.data['phone_number'], 
                      password = pwd_context.hash(request.parameter.data['password']),
                      first_name = request.parameter.data['first_name'],
                      last_name = request.parameter.data['last_name'])
        UsersRepo.insert(db, _user)
        return ResponseSchema(code='200', status='OK', message="success save data").dict(exclude_none=True)
    except Exception as error:
        return ResponseSchema(code='200', status='Error', message="Internal Server Error").dict(exclude_none=True)



@router.post('/login')
async def login(request:RequestSchema, db:Session = Depends(get_db)):
    try:
        _user = UsersRepo.find_by_username(db, Users, request.parameter.data["username"])
        if not pwd_context.verify(request.parameter.data['password'], _user.password):
            return ResponseSchema(code = "400", status="Bad Request", message = "invalid password").dict(exclude_none=True)
        
        token = JWTRepo.generete_token({'sub':_user.username})
        return ResponseSchema(code="200", status="OK", message="success login!", result=TokenResponse(access_token=token, token_type="Bearer")).dict(exclude_none=True)
    except Exception as error:
        error_message = str(error.args)
        return ResponseSchema(code="500", status = "Internal Server Error", message="Internal Server Error").dict(exclude_none=True)
    
    
@router.get('/users', dependencies=[Depends(JWTBearer())])
async def retrieve_all(db: Session = Depends(get_db)):
    _user = UsersRepo.retrieve_all(db, Users)
    return ResponseSchema(code = "200", status="OK", message="Success retrieve data", result = _user).dict(exclude_none=True)