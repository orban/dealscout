## Introduction

Welcome to DealScout, an innovative open-source project designed to revolutionize the online shopping experience. Developed during a recent SPC / OpenAI hackathon by a team led by an experienced open-source developer, DealScout leverages cutting-edge AI technologies to offer a unique service. By allowing users to submit a photo and a description of an item via WhatsApp, DealScout simplifies the search process across online marketplaces, using advanced AI to find the best deals that match the user's request. Our mission is to make online shopping more accessible, efficient, and tailored to individual needs.

## Features

DealScout integrates several key technologies and features to provide a seamless shopping experience:

- **WhatsApp Integration**: Users can easily submit their shopping requests via WhatsApp, making the service accessible and convenient.
- **AI-Powered Image and Description Analysis**: Utilizing the latest GPT-4V for vision analysis, DealScout accurately understands and processes user submissions.
- **Automated Online Marketplace Search**: Through the MultiOn API, the system automates the search across multiple online marketplaces, translating user queries into specific search URLs.
- **Image Scraping and Comparison**: DealScout scrapes product images from search results and uses AI to compare these with the user's submitted photo, ranking results by similarity.
- **Seller Verification**: Before finalizing a deal, the system contacts sellers to verify the availability and legitimacy of items.
- **User Notification**: Users are informed about potential deals, streamlining the decision-making process.

## Getting Started

### Prerequisites

To use DealScout, you'll need:

- Python 3.11 installed on your machine.
- Accounts with WhatsApp, OpenAI, and MultiOn for API access.
- Basic knowledge of Python and command-line tools.

### Installation Instructions

1. **Clone the Repository**: Start by cloning the DealScout repository to your local machine using Git:

```bash
git clone https://github.com/orban/dealscout.git
cd dealscout
```

2. **Install Dependencies**: With Poetry installed, run the following command to install the necessary dependencies:

```bash
poetry install
```

3. **Configure API Keys**: You'll need to set up your API keys for OpenAI and MultiOn. Create a `.env` file in the root directory and add your keys:

```plaintext
OPENAI_API_KEY=your_openai_api_key_here
MULTION_API_KEY=your_multion_api_key_here
WHATSAPP_API_KEY=your_whatsapp_api_key_here
```

4. **Configure WhatsApp Integration**: Follow the documentation provided by WhatsApp to set up your integration and connect it to DealScout.

### Usage Guide

To start the DealScout service, run:

```bash
poetry run uvicorn api.main:app
```

Users can interact with DealScout by sending a WhatsApp message to the configured number. The message should include a photo of the item they're searching for, along with a brief description. DealScout will process the request and reply with potential deals.

**Example Message**:

"Hi DealScout, I'm looking for a pair of vintage Nike sneakers, preferably in size 10. Attached is a photo for reference."

## Contributing

We welcome contributions from developers of all skill levels. To get involved:

- **Suggest Features or Report Issues**: Use the GitHub issues page to suggest new features or report bugs.
- **Submit Pull Requests**: Feel free to fork the repository and submit pull requests with your improvements.
- **Spread the Word**: Share DealScout with your friends and colleagues to help us grow the community.


## License

DealScout is released under the [MIT License](LICENSE). This license permits anyone to use, modify, distribute, and sublicense the project, provided that the original copyright and license notice are included.

---

This README aims to provide all the necessary information to understand, use, and contribute to DealScout effectively. We strive to make this document as clear and concise as possible, but if you have any questions or need further clarification, please don't hesitate to reach out or open an issue on GitHub.