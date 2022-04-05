from pydantic import BaseModel, validator


class Pin(BaseModel):
    img_url: str
    title: str
    description: str

    @validator('title', 'description')
    def to_ascii(cls, row_string: str):
        if row_string.isascii():
            return row_string
        new_sting = []
        for char in row_string:
            if char.isascii():
                new_sting.append(char)
                continue
            if char == '—':
                new_sting.append('-')
        return ''.join(new_sting)
