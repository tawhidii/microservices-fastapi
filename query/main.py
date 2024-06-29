from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import Dict, List
import httpx
import uvicorn

app = FastAPI(title="Query Service")


class Post(BaseModel):
    id: str
    title: str
    comments: List[Dict[str, str]] = []


class Comment(BaseModel):
    id: str
    content: str
    status: str


class Event(BaseModel):
    type: str
    data: Dict[str, str]


posts: Dict[str, Post] = {}


def handle_event(event_type: str, data: Dict[str, str]):
    if event_type == "PostCreated":
        post = Post(id=data['id'], title=data['title'])
        posts[post.id] = post

    elif event_type == "CommentCreated":
        comment = Comment(**data)
        post = posts.get(data['postId'])
        if post:
            post.comments.append(comment.dict())
        else:
            raise HTTPException(status_code=404, detail="Post not found")

    elif event_type == "CommentUpdated":
        post = posts.get(data['postId'])
        if post:
            comment = next((c for c in post.comments if c['id'] == data['id']), None)
            if comment:
                comment.update(content=data['content'], status=data['status'])
            else:
                raise HTTPException(status_code=404, detail="Comment not found")
        else:
            raise HTTPException(status_code=404, detail="Post not found")


@app.get("/posts")
async def get_posts():
    return posts


@app.post("/events")
async def handle_events(event: Event):
    handle_event(event.type, event.data)
    return {}


@app.on_event("startup")
async def startup_event():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:4005/events")
            response.raise_for_status()
            events = response.json()
            for event in events:
                handle_event(event['type'], event['data'])
    except httpx.HTTPStatusError as exc:
        print(f"HTTP error occurred: {exc.response.status_code} - {exc.response.text}")
    except Exception as exc:
        print(f"An error occurred: {exc}")


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=4002)
