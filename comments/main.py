from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from uuid import uuid4
import httpx

app = FastAPI(title="Comment Service")

comments_by_post_id = {}


class Comment(BaseModel):
    id: str
    content: str
    status: str


class CommentCreateRequest(BaseModel):
    content: str


class Event(BaseModel):
    type: str
    data: dict


@app.get("/posts/{id}/comments")
async def get_comments(id: str):
    return comments_by_post_id.get(id, [])


@app.post("/posts/{id}/comments")
async def create_comment(id: str, request: CommentCreateRequest):
    comment_id = str(uuid4())
    comment = Comment(id=comment_id, content=request.content, status="pending")

    comments = comments_by_post_id.get(id, [])
    comments.append(comment)
    comments_by_post_id[id] = comments

    event = {
        "type": "CommentCreated",
        "data": {
            "id": comment_id,
            "content": comment.content,
            "postId": id,
            "status": comment.status,
        },
    }

    async with httpx.AsyncClient() as client:
        await client.post("http://localhost:4005/events", json=event)

    return comments


@app.post("/events")
async def handle_event(event: Event):
    print("Event Received:", event.type)

    if event.type == "CommentModerated":
        data = event.data
        post_id = data["postId"]
        comment_id = data["id"]
        status = data["status"]
        content = data["content"]

        comments = comments_by_post_id.get(post_id, [])
        comment = next((c for c in comments if c.id == comment_id), None)

        if comment:
            comment.status = status

            updated_event = {
                "type": "CommentUpdated",
                "data": {
                    "id": comment_id,
                    "status": status,
                    "postId": post_id,
                    "content": content,
                },
            }

            async with httpx.AsyncClient() as client:
                await client.post("http://localhost:4005/events", json=updated_event)

    return {}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=4001)
