from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn
from codeshieldapp.service.bash_scanner import BashScanService
from fastapi import Depends

app = FastAPI()

@app.post("/process")
async def process_text(
    data: dict, bash_scan_service: BashScanService = Depends(BashScanService())
):
    text = data.get("text")
    if not text:
        return {"error": "No text provided"}

    return await bash_scan_service.scan_bash_cmd(text)


@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    bash_scan_service: BashScanService = Depends(BashScanService()),
):
    await websocket.accept()
    try:
        while True:
            text = await websocket.receive_text()
            result = await bash_scan_service.scan_bash_cmd(text)
            await websocket.send_json(result)

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await websocket.send_json({"error": str(e)})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
