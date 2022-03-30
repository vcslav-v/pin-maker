import os
import secrets

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from pin_maker import schemas
from pin_maker.api import service

router = APIRouter()
security = HTTPBasic()

username = os.environ.get('API_USERNAME') or 'root'
password = os.environ.get('API_PASSWORD') or 'pass'


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, username)
    correct_password = secrets.compare_digest(credentials.password, password)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Basic'},
        )
    return credentials.username


@router.post('/make-plus-pin')
def make_plus_pin(raw_pin: schemas.Pin, _: str = Depends(get_current_username)):
    pin = service.make_plus_pin(raw_pin)
    return Response(
        content=pin,
        media_type='image/png',
        headers={
            'Content-Disposition': 'attachment; filename=result.png',
            'pin-title': raw_pin.title,
            'pin-description': raw_pin.description,
        }
    )
