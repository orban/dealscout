import os
from typing import Any

import multion
from asgiref.sync import sync_to_async


class MarketplaceAssistant:
    """
    A class to interact with Facebook Marketplace using the Multion API to find deals
    and return structured data.
    """

    OPENAI_MODEL_NAME: str = os.getenv("OPENAI_MODEL_NAME", "text-davinci-003")
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    DATA_LOCATION: str | None = os.getenv("DATA_LOCATION")

    def __init__(self) -> None:
        multion.login()
        self.prefix: str = (
            "You are a Opal, a personal assistant interacting in a conversation with your "
            "human companion to help them find deals on Facebook Marketplace. "
            "You are given the task to find all of the matching results and returning "
            "data for each result. For each matching item in the marketplace, return well-structured JSON with the following form:\n\n"
            "[\n"
            " {\n"
            "    'title': title,\n"
            "    'url': url,\n"
            "    'price': price,\n"
            "    'location': location,\n\n"
            " }\n"
            "]\n\n"
            "The URL should be the link to the photo of the item. The price should be the price of the item. The location should be the location of the item. The title should be the title of the item."
            "YOU MUST RETURN THE DATA IN THE FORMAT ABOVE."
        )

    @sync_to_async
    def query(self, prompt: str) -> Any:
        """
        Logs into Multion and uses it to browse Facebook Marketplace with a given prompt.

        :param prompt: The prompt to be used for the Multion API.
        :return: The result of the Multion browsing operation.
        """

        full_prompt = f"{self.prefix} {prompt} Look at the results. Based on the preferences of the user, select the top three matches. Visit each of those pages and return well-structured JSON with the following format: [{'title', 'url', 'price', 'location'}]."
        return multion.browse(
            {
                "cmd": full_prompt,
                "url": "https://www.facebook.com/marketplace/sanfrancisco",
                "maxSteps": 100,
            }
        )
