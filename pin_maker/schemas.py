from pydantic import BaseModel


class Pin(BaseModel):
    img_url: str
    title: str
    description: str
