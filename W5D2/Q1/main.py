from fastapi import FastAPI
from iers.worker import process_batch

app = FastAPI(title="IERS")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/run-batch")
def run_batch():
    process_batch()
    return {"status": "batch processed"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 