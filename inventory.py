from models import db, Item, validate_item_id, MONGO_ID
from fastapi import HTTPException, Depends
from mysecurity import get_current_user
from bson import ObjectId
from models import User

def add_inventory_routes(app):
    # create item POST
    # making type annotations making a variable for fastapi
    @app.post('/inventory', tags=["Inventory"], status_code=201)
    async def create_item(item: Item, user: User = Depends(get_current_user)):
        if hasattr(item, 'id'):
            delattr(item, 'id')

        item.user_id = str(user['_id'])
        item.date = str(item.date)

        result = db.inventory.insert_one(item.dict(by_alias=True))
        if not result.acknowledged:
            raise HTTPException(400, 'Unable to create item')

        item.id = result.inserted_id
        return item
    
    @app.get('/inventory/{item_id}', tags=['Inventory'], description='Get an inventory item by its ID', status_code=200)
    async def get_item(item_id: str, user: User = Depends(get_current_user)):
        validate_item_id(item_id)
        
        item = db.inventory.find_one({'_id': ObjectId(item_id), 'user_id': str(user['_id'])})

        if not item:
            raise HTTPException(404, "Item not found")
    
        item['id'] = str(item['_id'])
        del item['_id']

        return item

        

    # making type annotations making a variable for fastapi
    @app.patch('/inventory/{item_id}', tags=["Inventory"], description="A more detailed description goes here.....", status_code=201)
    async def update_item(item_id: str, item: Item, user: User = Depends(get_current_user)):
        validate_item_id(item_id)

        if hasattr(item, 'id'):
            delattr(item, 'id')
            
        # finding item to update in the database to validate that it exists
        stored_item = db.inventory.find_one({MONGO_ID: ObjectId(item_id), 'user_id': str(user['_id'])})
        if stored_item is None:
            raise HTTPException(404, "Item not found")

        # Add user_id to the update object so it wont get overwritten
        update = item.dict(by_alias=True)
        update["user_id"] = str(user['_id'])
        update['date'] = str(item.date)
        
        #need to tell mongo what to do, $set makes it update all values that match update object
        result = db.inventory.update_one({MONGO_ID: ObjectId(item_id)}, { "$set": update})
        
        if not result.acknowledged:
            raise HTTPException(400, 'Unable to update item')
            
        item.id = ObjectId(item_id)
        item.user_id = user['_id']

        return item

    @app.delete('/inventory/{item_id}', tags=["Inventory"], status_code=200)
    async def delete_item(item_id: str, user: User = Depends(get_current_user)):
        validate_item_id(item_id)

        stored_item = db.inventory.find_one({MONGO_ID: ObjectId(item_id), 'user_id': str(user['_id'])})
        if stored_item is None:
            raise HTTPException(404, "Item not found")

        result = db.inventory.delete_one({MONGO_ID: ObjectId(item_id)})

        if result.deleted_count == 0:
          raise HTTPException(400, 'Unable to delete item')

    # get all inventory items by user
    @app.get('/inventory', tags=["Inventory"], description="A more detailed description goes here.....")
    async def get_inventory(user: User = Depends(get_current_user)):
        items = []
        for item in db.inventory.find({'user_id': str(user['_id'])}):
            item['id'] = str(item['_id'])
            del item['_id']
            items.append(item)
        return items    
