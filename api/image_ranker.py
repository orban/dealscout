from openai import OpenAI
import json


class ImageRanker:
    def __init__(self):
        # Initialize OpenAI client
        self.client = OpenAI()

    def construct_prompt(self, references, items):
        message_array = [
            {
                "type": "text",
                "text": f"""The next {len(references)} images are the style I like and I'm looking to buy something in that style. """,
            }
        ]
        for reference in references:
            message_array.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": reference,
                    },
                },
            )

            message_array.append(
                {
                    "type": "text",
                    "text": """The following images are items I'm considering buying.
                        Return a ranked json list of the items. 
                        It should include the item name, index, rank, and whether I should buy it (be very discerning. I only want to buy stuff that fits my style). 
                        Do not include any other thinking or information before or after the json.
                        The json format is:
                        index: [item index]
                        item_name: [string]
                        rank: [item rank]
                        buy: True/False
                        """,
                },
            )

        for index, item in enumerate(items[0:5]):
            message_array.append(
                {
                    "type": "text",
                    "text": f"The following item has an item_name of {item['product_name']} and has index {index}",
                },
            )
            message_array.append(
                {
                    "type": "image_url",
                    "image_url": {"url": item["image_url"]},
                },
            )

        try:
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {"role": "user", "content": message_array}
                ],
                max_tokens=4000,
            )
            return response.choices[0].message.content
        except Exception as e:
            return {"error": str(e)}

    def convert_to_json(self, message):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "parse this message and extract the json from it",
                },
                {"role": "user", "content": message},
            ],
        )
        return json.loads(response.choices[0].message.content)

    def rank_images(self, reference_image_urls: list, items: list):
        try:

            response = self.construct_prompt(reference_image_urls, items)
            ranking = self.convert_to_json(response)
            buy_items = [
                items[i["index"]]['page_url'] for i in ranking["data"] if i["buy"]
            ]

            return buy_items
        except Exception as e:
            raise e
