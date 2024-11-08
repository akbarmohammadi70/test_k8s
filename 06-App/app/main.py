from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import geoip2.database
import psycopg2
from psycopg2 import sql
from contextlib import closing
import os

app = FastAPI()

DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "app")
DB_USER = os.getenv("POSTGRES_USER", "app")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "qazwsxedc")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

class IPAddress(BaseModel):
    ip: str

@app.get("/country/{ip}")
async def get_country(ip: str):
    try:
        geoip_db_path = '/app/GeoLite2-Country.mmdb' 
        if not os.path.exists(geoip_db_path):
            raise HTTPException(status_code=500, detail="GeoIP database file not found")
        
        with geoip2.database.Reader(geoip_db_path) as reader:
            response = reader.country(ip)
            country_name = response.country.name
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error in GeoIP lookup: {e}")
    
    try:
        with closing(get_db_connection()) as conn:
            with conn.cursor() as cursor:
                query = sql.SQL("INSERT INTO ip_country (ip, country) VALUES (%s, %s) "
                                "ON CONFLICT (ip) DO UPDATE SET country = EXCLUDED.country")
                cursor.execute(query, (ip, country_name))
                conn.commit()

                cursor.execute("SELECT ip, country FROM ip_country WHERE ip = %s", (ip,))
                saved_data = cursor.fetchone()

            if saved_data:
                return {"ip": saved_data[0], "country": saved_data[1]}
            else:
                raise HTTPException(status_code=404, detail="Data not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@app.on_event("startup")
async def startup():
    try:
        with closing(get_db_connection()) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ip_country (
                        ip VARCHAR(45) PRIMARY KEY,
                        country VARCHAR(255) NOT NULL
                    );
                """)
                conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database initialization error: {e}")


