import json
import logging
import asyncio
from plug_sdk.sdk import PlugSDK
from plug_sdk.quotation_transmission.schemas import (
    TransmissionRequest,
    TransmissionResponse,
)

logger = logging.getLogger("async_client")

logger.setLevel(logging.DEBUG)


async def main():
    plug = PlugSDK(base_url="http://uatplug.essor.net/")
    # plug = PlugSDK(base_url="http://localhost:8000/")
    with open("transmit_quotation_request_data.json", "r") as f:
        request_data = json.load(f)

    request_data['data']['section_number'] = 2
    del request_data['data']['secao']
    request = TransmissionRequest(**request_data)
    response: TransmissionResponse = await plug.transmit_quotation(request)
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
