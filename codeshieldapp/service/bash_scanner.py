import httpx
from fastapi import Depends

from codeshieldapp.service.config import ApplicationConfig


class BashScanService:
    def __init__(self, appcfg: ApplicationConfig = None):
        self.cfg = appcfg.cfg if appcfg is not None else None
        self.client = httpx.AsyncClient()

    async def scan_bash_cmd(self, text: str):
        try:
            # Step 1: Send text to encoding-service
            print(text)
            encoding_response = await self.client.post(
                self.cfg["services"]["bash"]["encoder"],
                json={"code": text},
            )
            encoding_response.raise_for_status()
            encoded_data = {"encoding": [encoding_response.json()]}

            # Step 2: Send encoded data to classifier-service
            classifier_response = await self.client.post(
                self.cfg["services"]["bash"]["classifier"], json=encoded_data
            )
            classifier_response.raise_for_status()
            classification = classifier_response.json()
            return classification

        except httpx.HTTPStatusError as e:
            return {
                "error": f"HTTP error: {e.response.status_code}",
                "details": e.response.text,
            }
        except Exception as e:
            return {"error": f"Processing failed: {str(e)}"}

    def __call__(self, appcfg: ApplicationConfig = Depends(ApplicationConfig())):
        self.cfg = appcfg.cfg
        self.client = httpx.AsyncClient()
        return self
