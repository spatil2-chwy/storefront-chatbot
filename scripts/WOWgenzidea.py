import base64
from openai_client import get_openai_client

client = get_openai_client()

prompt = """
A cute picture of a Labrador Retriever wearing a birthday hat.
"""

result = client.images.generate(
    model="gpt-image-1",
    prompt=prompt
)

image_base64 = result.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

# Save the image to a file
with open("otter.png", "wb") as f:
    f.write(image_bytes)