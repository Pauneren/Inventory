from models import db, User, UserOut, validate_user_email, MONGO_ID
from mysecurity import get_current_user, get_password_hash
from fastapi import HTTPException, Depends

def add_users_routes(app):
    # to create a user
    @app.post('/users', tags=["Users"], summary="Create a user", response_model=UserOut, status_code=201)
    async def create_user(user: User):
        if hasattr(user, 'id'):
            delattr(user, 'id')

        # check if email is valid
        validate_user_email(user.email)

        # check if email is already in use
        try:
            email_user = db.users.find_one({'email': user.email})
        except Exception:
            raise HTTPException(500, "Internal Server Error")
        if email_user:
            raise HTTPException(409, "This email is already in use")

        # hash password
        user.password = get_password_hash(user.password)

        # insert user into MongoDB
        try:
            db.users.insert_one(dict(user))
        except Exception as e:
            raise HTTPException(500, "Internal Server Error")

        # return the newly created user to the client
        return dict(user)


    @app.get('/users', tags=["Users"], status_code=200)
    async def get_user(user: User = Depends(get_current_user)):
        user['id'] = str(user['_id'])
        del user['_id']
        del user['password']
        return user


    # to delete a user
    @app.delete('/users', tags=["Users"], status_code=200)
    async def delete_user(user: User = Depends(get_current_user)):
        result = db.users.delete_one({MONGO_ID: user[MONGO_ID]})

        if result.deleted_count == 0:
            raise HTTPException(400, 'Unable to delete')
