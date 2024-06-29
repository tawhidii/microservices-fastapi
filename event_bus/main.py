from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import uvicorn

app = FastAPI(title="Event Bus")

events = []


class Event(BaseModel):
    type: str
    data: dict


@app.post("/events")
async def receive_event(event: Event):
    events.append(event.dict())
    urls = [
        "http://localhost:4000/events",
        "http://localhost:4001/events",
        "http://localhost:4002/events",
        "http://localhost:4003/events"
    ]
    print(event.dict())

    async with httpx.AsyncClient() as client:
        for url in urls:
            try:
                await client.post(url, json=event.dict())
            except httpx.RequestError as e:
                print(f"An error occurred while requesting {url}: {e}")

    return {"status": "OK"}


@app.get("/events")
async def get_events():
    return events


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=4005)
