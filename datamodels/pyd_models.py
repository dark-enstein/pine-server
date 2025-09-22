from pydantic import BaseModel, ConfigDict
class SolubilityParams(BaseModel):
    seq: str

class ProtProtInteraction(BaseModel):
    seq_1: str
    seq_2: str

class UserRequest(BaseModel):
    name: str