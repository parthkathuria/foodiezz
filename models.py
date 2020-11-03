from pydantic import BaseModel


class SocrataData(BaseModel):
    """
    The model class for defining the Socrata data that you will receive from SODA API
    """
    applicant: str
    location: str
    start24: str
    end24: str
    dayorder: int
    dayofweekstr: str
