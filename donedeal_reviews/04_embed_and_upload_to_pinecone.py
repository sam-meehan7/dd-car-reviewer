import os
import json
import time
from pinecone import Pinecone
from dotenv import load_dotenv
import pandas as pd

from langchain.embeddings.openai import OpenAIEmbeddings
from tqdm.auto import tqdm

load_dotenv()

# Initialize Pinecone
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])

index_name = "donedeal-car-reviews"

embed_model = OpenAIEmbeddings(model="text-embedding-3-small")

# connect to index
index = pc.Index(index_name)
time.sleep(1)
# view index stats
index.describe_index_stats()

with open("data/youtube-transcriptions-part-2.jsonl", "r", encoding="utf-8") as f:
    dataset = [json.loads(line) for line in f]

data = pd.DataFrame(dataset)

batch_size = 100

for batch_start in tqdm(range(0, len(data), batch_size)):
    batch_end = min(len(data), batch_start + batch_size)
    # get batch of data
    data_batch = data.iloc[batch_start:batch_end]
    # generate unique ids for each chunk
    unique_ids = [data_row["id"] for _, data_row in data_batch.iterrows()]
    # get text to embed
    text_to_embed = [data_row["text"] for _, data_row in data_batch.iterrows()]
    # embed text
    embedded_text = embed_model.embed_documents(text_to_embed)
    # Create metadata dictionary
    pinecone_metadata = [
        {
            "text": data_row["text"],
            "url": data_row["url"],
            "start": data_row["start"],
            "end": data_row["end"],
            "title": data_row["title"],
            "thumbnail": data_row["thumbnail"],
            "author": data_row["author"],
            "channel_id": data_row["channel_id"],
            "channel_url": data_row["channel_url"],
        }
        for _, data_row in data_batch.iterrows()
    ]

    # Add to Pinecone
    index.upsert(vectors=zip(unique_ids, embedded_text, pinecone_metadata))
