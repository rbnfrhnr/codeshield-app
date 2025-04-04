from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import httpx
import uvicorn

app = FastAPI()

# Global HTTP client for persistent connections
client: httpx.AsyncClient = None

@app.on_event("startup")
async def startup():
    global client
    client = httpx.AsyncClient()

@app.on_event("shutdown")
async def shutdown():
    await client.aclose()

async def process_text_logic(text: str):
    """
    Handles the full text processing pipeline:
    1. Sends the text to encoding-service.
    2. Uses the encoded response to request classification from classifier-service.
    3. Returns the final classification result.
    """
    try:
        # Step 1: Send text to encoding-service
        print(text)
        encoding_response = await client.post("http://37.156.42.24:30080/predictions/bash-encoder", json={"code": text})
        encoding_response.raise_for_status()
        encoded_data = {
            "encoding": [encoding_response.json()]
        }
        # Step 2: Send encoded data to classifier-service
        classifier_response = await client.post("http://37.156.40.174:30008/classify", json=encoded_data)
        classifier_response.raise_for_status()
        classification =  classifier_response.json()
        return classification

    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP error: {e.response.status_code}", "details": e.response.text}
    except Exception as e:
        return {"error": f"Processing failed: {str(e)}"}

@app.post("/process")
async def process_text(data: dict):
    """
    HTTP endpoint that accepts text input, processes it, and returns classification results.
    """
    text = data.get("text")
    if not text:
        return {"error": "No text provided"}
    
    return await process_text_logic(text)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time text processing.
    """
    await websocket.accept()
    try:
        while True:
            text = await websocket.receive_text()
            result = await process_text_logic(text)
            await websocket.send_json(result)

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await websocket.send_json({"error": str(e)})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)