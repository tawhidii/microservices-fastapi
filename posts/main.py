from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Dict
import httpx
import uuid

app = FastAPI(title="Post service")

posts: Dict[str, Dict[str, str]] = {}


class Post(BaseModel):
    title: str


class Event(BaseModel):
    type: str
    data: Dict[str, str]


@app.get("/posts")
async def get_posts():
    return posts


@app.post("/posts", status_code=201)
async def create_post(post: Post):
    post_id = uuid.uuid4().hex[:8]
    post_data = {
        "id": post_id,
        "title": post.title
    }
    posts[post_id] = post_data

    event = {
        "type": "PostCreated",
        "data": post_data
    }

    async with httpx.AsyncClient() as client:
        try:
            await client.post("http://localhost:4005/events", json=event)
        except httpx.RequestError:
            raise HTTPException(status_code=500, detail="Event service is down")

    return post_data


@app.post("/events")
async def handle_event(event: Event):
    print(f"Received Event: {event.type}")
    return {}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=4000)
