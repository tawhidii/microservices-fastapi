from fastapi import FastAPI, Request
from pydantic import BaseModel
import httpx

app = FastAPI(title="Moderation Service")


class CommentData(BaseModel):
    id: str
    postId: str
    content: str


class Event(BaseModel):
    type: str
    data: CommentData


@app.post("/events")
async def handle_event(event: Event):
    if event.type == "CommentCreated":
        status = "rejected" if "orange" in event.data.content else "approved"

        async with httpx.AsyncClient() as client:
            await client.post("http://localhost:4005/events", json={
                "type": "CommentModerated",
                "data": {
                    "id": event.data.id,
                    "postId": event.data.postId,
                    "status": status,
                    "content": event.data.content
                }
            })

    return {}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=4003)
