from fastapi import FastAPI
from api import auth, order, profile, product, store
import uvicorn
from admin.setup import admin_setup

app = FastAPI(title='Delivery Operator')
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(product.router)
app.include_router(store.router)
app.include_router(order.router)
admin_setup(app=app)

if __name__ == '__main__': uvicorn.run('main:app', reload=True)