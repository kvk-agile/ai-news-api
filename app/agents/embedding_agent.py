from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()


def create_embedding(text: str) -> list[float]:
    """Convert a piece of text into its embedding (a list of 1536 numbers)."""

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )

    return response.data[0].embedding