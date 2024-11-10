```markdown
IP Country Lookup API

This project is a simple API built with FastAPI that can retrieve country information for an IP address using the GeoIP2 database and store this data in a PostgreSQL database.

Prerequisites

Before running the project, make sure you have the following installed on your system:

- Python 3.10 or higher
- Docker (for running the project in isolated environments)
- PostgreSQL
```
### Installation and Setup

### 1. Install Dependencies

First, to install the project dependencies, navigate to the project directory and run the following command:

```bash
pip install -r requirements.txt
```

### 2. PostgreSQL Database Setup

Ensure that your PostgreSQL database is properly configured. You should set the following environment variables or use a `.env` file to configure them:

- `POSTGRES_HOST`: The database host address (default: `localhost`)
- `POSTGRES_PORT`: The database port (default: `5432`)
- `POSTGRES_DB`: The database name (default: `app`)
- `POSTGRES_USER`: The username for database connection (default: `app`)
- `POSTGRES_PASSWORD`: The password for database connection (default: `qazwsxedc`)

### 3. Database Initialization

The application will automatically create the `ip_country` table in your PostgreSQL database at startup. This is done using FastAPI's `on_event` method.

### 4. Running the Project

To start the API, run the following command:

```bash
uvicorn main:app --reload
```

This will start the server at `http://127.0.0.1:8000`.

### 5. Using the API

Once the API is running, you can use the following endpoint to get the country of an IP address:

```http
GET /country/{ip}
```

For example, to get the country for the IP address `8.8.8.8`, you can run:

```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/country/8.8.8.8' \
  -H 'accept: application/json'
```

If the IP address is found in the GeoIP2 database and successfully saved to the PostgreSQL database, the response will be:

```json
{
  "ip": "8.8.8.8",
  "country": "United States"
}
```

If an error occurs (e.g., invalid IP or GeoIP2 database file not found), you'll receive an error message.

### 6. Docker Setup (Optional)

To run the project with Docker, you can use the provided Dockerfile. Build the Docker image and run the container with the following commands:

```bash
docker build -t ip-country-api .
docker run -p 8000:8000 ip-country-api
```

This will start the application inside a Docker container, and the API will be accessible at `http://127.0.0.1:8000`.

## Notes

- The `GeoLite2-Country.mmdb` file (GeoIP2 database) is required for the country lookup feature. Make sure to include it in your project directory.
- The application supports automatic table creation in PostgreSQL if the table doesn't already exist.
- For production use, consider adding proper error handling, logging, and security measures.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```

This `README.md` provides an overview of how to set up, run, and interact with the API, as well as how to use Docker for running the application in an isolated environment.