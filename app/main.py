from fastapi import FastAPI

app = FastAPI(title="Wine API", version="0.1.0")


@app.get("/")
def read_root():
    return {"message": "Welcome to Wine API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
