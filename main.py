from unittest.mock import Base
from fastapi import FastAPI
import asyncpg
import asyncio
from contextlib import asynccontextmanager
from pydantic import BaseModel
import json

class Item(BaseModel):
    id:int
    transcript:json

# postgres://user:password@host:port/database
DATABASE_URL = "postgresql://postgres:S%40ndhya281166@localhost:5432/transcript_db"

@asynccontextmanager
async def lifespan(app:FastAPI):
    try:
        db_pool = await asyncpg.create_pool(DATABASE_URL)
        app.state.db = db_pool

        async with app.state.db.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS transcripts (
                    id SERIAL PRIMARY KEY,
                    transcript VARCHAR(255)
                );
            """)

            # await conn.execute("""
            #     INSERT INTO transcripts (id,transcript) VALUES
            #                    (1,'hello darkness my old friend')
            # """)

        yield 

        await app.state.db.close()
    except Exception as e:
        print("Error: ",e)
    finally:
        print("Startup complete")

app = FastAPI(lifespan=lifespan)

@app.get('/transcripts')
async def get_transripts():
    async with app.state.db.acquire() as conn:
        result = await conn.fetch(
            """
            SELECT * from transcripts;
            """
        )
        return [dict(r) for r in result]

@app.post('/transcripts/')
async def post_transripts(obj:Item):
    print(obj)
    async with app.state.db.acquire() as conn:
        sql_statement =  """
            INSERT INTO transcripts (id,transcript) VALUES ($1,$2);
            """
        print(sql_statement)
        result = await conn.execute(sql_statement,obj.id,obj.transcript)
        return result
    
@app.delete('/transcript/{id}')
async def del_trancript(id:int):
    async with app.state.db.acquire() as conn:
        sql_statement =  """
            DELETE FROM transcripts WHERE id=$1;
            """
        # print(sql_statement)
        result = await conn.execute(sql_statement,id)
        return result


