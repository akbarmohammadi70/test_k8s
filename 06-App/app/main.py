from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
import geoip2.database
import psycopg2
from psycopg2 import sql
import os
from pydantic import BaseModel  # Add this import

# Initialize FastAPI app
app = FastAPI()

# Initialize Prometheus metrics instrumentation
instrumentator = Instrumentator()

# Configure Prometheus metrics exposure on `/metrics` endpoint
instrumentator.instrument(app).expose(app, "/metrics")

# Database configuration from environment variables
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "app")
DB_USER = os.getenv("POSTGRES_USER", "app")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "qazwsxedc")

# Connect to PostgreSQL database
def get_db_connection():
    connection = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return connection

# Data model for storing IP and country in the database
class IPAddress(BaseModel):
    ip: str

@app.get("/country/{ip}")
async def get_country(ip: str):
    # Read from GeoIP2 database
    try:
        reader = geoip2.database.Reader('GeoLite2-Country.mmdb')
        response = reader.country(ip)
        country_name = response.country.name
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error in GeoIP lookup: {e}")
    
    # Save to PostgreSQL database
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = sql.SQL("INSERT INTO ip_country (ip, country) VALUES (%s, %s) ON CONFLICT (ip) DO UPDATE SET country = EXCLUDED.country")
        cursor.execute(query, (ip, country_name))
        conn.commit()

        # Retrieve saved data
        cursor.execute("SELECT ip, country FROM ip_country WHERE ip = %s", (ip,))
        saved_data = cursor.fetchone()

        # Close database connection
        cursor.close()
        conn.close()

        if saved_data:
            return {"ip": saved_data[0], "country": saved_data[1]}
        else:
            raise HTTPException(status_code=404, detail="Data not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

# Initialize database table on startup
@app.on_event("startup")
async def startup():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ip_country (
                ip VARCHAR(45) PRIMARY KEY,
                country VARCHAR(255) NOT NULL
            );
        """)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database initialization error: {e}")

# Run the FastAPI app using Uvicorn
# uvicorn main:app --reload
