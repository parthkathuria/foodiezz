from pydantic import BaseModel


class SocrataData(BaseModel):
    applicant: str
    location: str
    start24: str
    end24: str
    dayorder: int
    dayofweekstr: str
