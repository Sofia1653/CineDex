from pydantic import BaseModel

class PeopleResponse(BaseModel):
    nome_pessoa: str
    tipo_pessoa: str
    sk_person_id: str

