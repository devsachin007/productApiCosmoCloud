from fastapi import FastAPI, Query, HTTPException
from urllib.parse import quote_plus
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from apiRouters.cosmoApi.routes import cosmo
app=FastAPI()

app.include_router(cosmo)



