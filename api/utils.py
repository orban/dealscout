import aiohttp
from loguru import logger


async def post_async(url, data, return_json=True) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            content_type = response.headers.get("Content-Type", "")
            if "application/json" in content_type:
                return await response.json() if return_json else await response.text()
            # Handle non-JSON responses appropriately
            response_text = await response.text()
            logger.info(
                f"Unexpected response MIME type: {content_type}, response: {response_text}"
            )
            return response_text


def list_to_str(lst: list) -> str:
    return ",".join(lst) if lst is not None else ""


def str_to_list(s: str) -> list:
    return s.split(",") if s else []
