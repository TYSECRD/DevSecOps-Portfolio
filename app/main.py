from fastapi import FastAPI

app = FastAPI(title="DevSecOps Portfolio API")


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/api/info")
def app_info():
    return {
        "name": "DevSecOps Portfolio API",
        "version": "1.0.0",
        "environment": "development"
    }


@app.get("/api/greet")
def greet(name: str):
    return {"message": f"Hello, {name}!"}