from fastapi import FastAPI

app = FastAPI(
        title="Car Brain",
        summary="""
The cloud interface for volkswagen's car brain challange
        """,
        version="0.1",
        )

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
