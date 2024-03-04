import json
import os
from typing import Any, Dict, Optional

import multion  # noqa
from asgiref.sync import async_to_sync, sync_to_async  # noqa
from loguru import logger  # noqa
from openai import OpenAI

# Utilize environment variables with Python 3.11's improved os.environ.get() method
OPENAI_MODEL_NAME: str = os.environ.get("OPENAI_MODEL_NAME", "gpt-3.5-turbo-0125")
OPENAI_API_KEY: Optional[str] = os.environ.get(
    "OPENAI_API_KEY",
)
DATA_LOCATION: Optional[str] = os.environ.get("DATA_LOCATION")

# Initialize the OpenAI client outside of the class to avoid reinitialization
openai_client: OpenAI = OpenAI(api_key=OPENAI_API_KEY)


class MarketplaceAssistant:
    """
    A class to interact with Facebook Marketplace using the Multion API to find deals
    and return structured data.
    """

    def __init__(self) -> None:
        multion.login()
        self.prefix: str = (
            "You are Opal, a personal assistant interacting in a conversation with your human companion to help them "
            "find matching products online. The human companion will provide you with a prompt, "
            "and you will use the Multion API to browse Facebook Marketplace with the given prompt."
        )

    def parse_input(self, input_str: str) -> str | None:
        if not input_str:
            return None
        logger.debug(f"Received input string: {input_str}")
        # Use the OpenAI API to parse the input string asynchronously
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL_NAME,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant designed to output JSON.",
                },
                {
                    "role": "user",
                    "content": f"Parse the following input and return the URL, and any errors if present. Return a well-formed JSON object with two keys: 'url' and 'errors'"
                    f"Input: {input_str}",
                },
            ],
        )
        logger.debug(f"Received response: {response}")
        return response.choices[0].message.content if response.choices else None

    @sync_to_async
    def filter(self, prompt: str) -> Dict[str, Any]:
        """
        Logs into Multion and uses it to browse Facebook Marketplace with a given prompt.

        :param prompt: The prompt to be used for the Multion API.
        :return: The result of the Multion browsing operation.
        """

        full_prompt = (
            f"{self.prefix} Prompt: {prompt} Using the Human's prompt, Opal will now browse "
            f"Facebook Marketplace to find matching products. Opal will then provide the human"
            f" with the marketplace URL with the appropriate filters applied. "
            f"If you're not able to find a filter, simply move on and make a note in 'errors'. "
            f"Your result should be in the following format: {{'url': 'URL', 'errors': ['ERRORS']}}"
        )
        logger.debug(f"Using prompt: {full_prompt}")
        response = multion.browse(
            {
                "cmd": full_prompt,
                "url": "https://www.facebook.com/marketplace/sanfrancisco",
                "maxSteps": 25,
            }
        )
        if not response:
            return {"url": "", "errors": ["No results found"]}
        logger.debug(f"Received response: {response}")
        if parsed_input := self.parse_input(response):
            return json.loads(parsed_input)
        return {"url": "", "errors": ["No results found"]}

    @sync_to_async
    def message_seller(self, url: str) -> Any:
        """
        Logs into Multion and uses it to message a seller on Facebook Marketplace.

        :param url: The URL of the seller to be messaged.
        :return: The result of the Multion messaging operation.
        """
        full_prompt = (
            f"{self.prefix} For the following URL, Opal will now message the seller with a personalized "
            f"message on Facebook Marketplace. URL: {url} If you're not able to message the seller, "
            f"simply move on and make a note in 'errors'. "
            f"Your result should be in the following format: {{'message': 'MESSAGE', 'errors': ['ERRORS']}}"
        )
        logger.debug(f"Using prompt: {full_prompt}")
        result = multion.browse(
            {
                "cmd": full_prompt,
                "url": url,
                "maxSteps": 10,
            }
        )
        logger.debug(f"Received response: {result}")
        return result
