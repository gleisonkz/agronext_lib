import json
from fastapi import FastAPI, Request
from plug_sdk.quotation_transmission import TransmissionRequest, TransmissionResponse

app = FastAPI()


async def print_request_data(title: str, request: Request):
    data = await request.json()
    with open(f"{title}_request_data.json", "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


@app.post("/propostas/agro")
async def transmit_quotation(request: Request):
    await print_request_data("transmit_quotation", request)
    return TransmissionResponse(
        code="0",
        message="Success",
        proposal_id="12345",
    )


@app.post("/propostas/agro/recusar")
async def reject_quotation(request: Request):
    await print_request_data("reject_quotation", request)
    return {"status": "received"}


@app.post("/apolices/agro")
async def issue_policy(request: Request):
    await print_request_data("issue_policy", request)
    return {"status": "received"}
