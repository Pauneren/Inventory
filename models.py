from email_validator import validate_email, EmailNotValidError
from pydantic import BaseModel, Field
from fastapi import HTTPException
from pymongo import MongoClient
from typing import Optional
from bson import ObjectId
import datetime
import os

client = MongoClient(os.environ['MONGODB_URI'])
db = client.database

MONGO_ID = "_id"
   
def validate_item_id(item_id: str):
    if not ObjectId.is_valid(item_id):
        raise HTTPException(400, 'Invalid item id')
    
def validate_user_id(user_id: str):
     if not ObjectId.is_valid(user_id):
        raise HTTPException(400, 'Invalid user id')

def validate_user_email(email: str):
    try:
        # Validate.
        valid = validate_email(email)

        # Update with the normalized form.
        email = valid.email
        print('eeee', email)
    except EmailNotValidError as e:
        # email is not valid, exception message is human-readable
        raise HTTPException(400, str(e))

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
    id: Optional[PyObjectId] = Field(alias=MONGO_ID)
    username: str
    email: str
    password: str

    #The inner class Config is used to define some configuration for the model. Here we tell Pydantic that we are using a custom type (by arbitrary_types_allowed) and also a mapping for JSON serialization (by json_encoders).
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }
        schema_extra = {
            "example": {
                "username": "str",
                "email": "str",
                "password": "str"
            }
        }

class UserOut(BaseModel):
    username: str
    email: str


class Item(BaseModel):
    id: Optional[PyObjectId] = Field(alias=MONGO_ID)
    item: str 
    date: datetime.date
    description: str
    type_of_item: str
    amount: int
    user_id: Optional[str]
    image: str
    location: str
    price: str
    

    #The inner class Config is used to define some configuration for the model. Here we tell Pydantic that we are using a custom type (by arbitrary_types_allowed) and also a mapping for JSON serialization (by json_encoders).
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }
        schema_extra = {
            "example": {
                "item": "Item name",
                "date": "2010-11-12",
                "description": "This is a description of the item",
                "type_of_item": "Painting",
                "amount": 1,
                "image": "string",
                "location": "In the gallery",
                "price": "1000 kr"
            }
        }
    
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None
    username: Optional[str] = None
