from pydantic import BaseModel, Field
from bson import ObjectId
from pymongo import MongoClient
from fastapi import HTTPException
from typing import Optional
import datetime, os
# import pymongo

client = MongoClient(os.environ['MONGODB_URI'])
db = client.database
   
def validate_item_id(item_id: str):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(400, 'Invalid item id')
    
def validate_user_id(user_id: str):
     if not ObjectId.is_valid(user_id):
        raise HTTPException(400, 'Invalid user id')

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    # The method validate is used to check if the data received is actually valid for this class.
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid objectid')
        return ObjectId(v)

    @classmethod
    # modify schema is to avoid an error when accessing the documentation
    def __modify_schema__(cls, field_schema):
        field_schema.update(type='string')

#MongoDB expects a field with the name _id, but Pydantic does not accept any field that starts with _. Then we create an alias so Pydantic can understand our document.

# creating a model
class User(BaseModel):
    id: Optional[PyObjectId] = Field(alias='_id')
    name: str
    email: str
    password: str

    #The inner class Config is used to define some configuration for the model. Here we tell Pydantic that we are using a custom type (by arbitrary_types_allowed) and also a mapping for JSON serialization (by json_encoders).
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }

class Item(BaseModel):
    id: Optional[PyObjectId] = Field(alias='_id')
    item: str
    date: str
    description: str
    type_of_item: str
    amount: int
    user_id: Optional[str]
    image: str
    #location: str
    

    #The inner class Config is used to define some configuration for the model. Here we tell Pydantic that we are using a custom type (by arbitrary_types_allowed) and also a mapping for JSON serialization (by json_encoders).
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }
        schema_extra = {
            "example": {
                "item": "test",
                "date": "string",
                "description": "string",
                "type_of_item": "string",
                "amount": 0,
                "image": "string"
            }
        }
    