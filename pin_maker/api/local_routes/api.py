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
    pin = service.make_pb_pin(raw_pin, mode='Plus')
    return Response(
        content=pin,
        media_type='image/png',
        headers={
            'Content-Disposition': 'attachment; filename=result.png',
        }
    )


@router.post('/make-premium-pin')
def make_premium_pin(raw_pin: schemas.Pin, _: str = Depends(get_current_username)):
    pin = service.make_pb_pin(raw_pin, mode='Premium')
    return Response(
        content=pin,
        media_type='image/png',
        headers={
            'Content-Disposition': 'attachment; filename=result.png',
        }
    )


@router.post('/make-freebie-pin')
def make_freebie_pin(raw_pin: schemas.Pin, _: str = Depends(get_current_username)):
    pin = service.make_pb_pin(raw_pin, mode='Freebie')
    return Response(
        content=pin,
        media_type='image/png',
        headers={
            'Content-Disposition': 'attachment; filename=result.png',
        }
    )


@router.post('/make-td-pin')
def make_td_pin(raw_pin: schemas.Pin, _: str = Depends(get_current_username)):
    pin = service.make_td_pin(raw_pin)
    return Response(
        content=pin,
        media_type='image/png',
        headers={
            'Content-Disposition': 'attachment; filename=result.png',
        }
    )


@router.post('/make-td-mov-pin')
def make_td_mov_pin(raw_pin: schemas.MovePin, _: str = Depends(get_current_username)):
    pin = service.make_td_mov_pin(raw_pin)
    return Response(
        content=pin,
        media_type='video/mp4',
        headers={
            'Content-Disposition': 'attachment; filename=result.png',
        }
    )


@router.post('/parse-items-from-td-collection')
def parse_items_from_td_collection(article_link: str, _: str = Depends(get_current_username)) -> schemas.PinList:
    raw_pins = service.get_raw_pins(article_link)
    return raw_pins
