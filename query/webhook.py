from fastapi import FastAPI, Request, HTTPException
import json

app = FastAPI()

@app.post("/webhook")
async def webhook_listener(request: Request):
    try:
        # Parse the incoming JSON payload
        payload = await request.json()
        print("Received payload:", json.dumps(payload, indent=4))

        # Process the payload as needed
        # Here, you can add your business logic

        # Respond with a success message
        return {"message": "Webhook received successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Run the app using uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
