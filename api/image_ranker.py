from openai import OpenAI
import base64
import json

class ImageRanker:
    def __init__(self):
        # Initialize OpenAI client
        self.client = OpenAI()

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')


    def construct_prompt(self, references, consideration, base64_image):
        message_array = [
            {
                "type": "text",
                "text": f"""The first {len(references)} images are the style I like and I'm looking to buy something in that style. 
                            The last image contains five other items I'm considering. 
                            Return a ranked json list of the five items in the last image. 
                            It should include the item index, rank, and whether I should buy it (be very discerning). 
                            Do not include any other thinking or information before or after the json
                            The json format is:
                            index: [item index]
                            rank: [item rank]
                            buy: True/False
                            """,
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
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"
                },
            },
        )

        response = self.client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": message_array,
                }
            ],
            max_tokens=4000,
        )
        return response.choices[0].message.content

    def rank_images(self, reference_image_urls: list, consideration_image_urls: list, image_path: str):
        try:
            # Getting the base64 string
            base64_image = self.encode_image(image_path)
            
            # Constructing the prompt
            response = self.construct_prompt(reference_image_urls, consideration_image_urls, base64_image)
            
            # Convert the response to JSON
            json_response = json.loads(response)
            
            return json_response
        except Exception as e:
            raise e