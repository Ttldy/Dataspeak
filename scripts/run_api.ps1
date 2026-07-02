$ErrorActionPreference = "Stop"
uvicorn dataspeak.app.main:app --host 127.0.0.1 --port 18088
