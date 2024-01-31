import os
from pinecone import Pinecone as PineconePincone

from langchain_community.vectorstores import Pinecone as VectorstorePinecone
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

from dotenv import load_dotenv
import cohere

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

load_dotenv()

os.environ["COHERE_API_KEY"] = os.getenv("COHERE_API_KEY")
# init client
co = cohere.Client(os.environ["COHERE_API_KEY"])

chat = ChatOpenAI(openai_api_key=os.environ["OPENAI_API_KEY"], model='gpt-4-0125-preview', temperature=0.1, max_tokens=3500)

pc = PineconePincone(api_key=os.environ["PINECONE_API_KEY"])
index = pc.Index("donedeal-car-reviews")

embed_model = OpenAIEmbeddings(model="text-embedding-3-small")

text_field = "text"  # the metadata field that contains our text

# pylint: disable=not-callable
vectorstore = VectorstorePinecone(index, embed_model.embed_query, text_field)


def search_vectorstore(query: str):
    results = vectorstore.similarity_search(query, k=25)

    # Convert results to format suitable for Cohere reranking
    documents_to_rerank = [{"text": result.page_content} for result in results]

    # Use Cohere to rerank the documents
    reranked_response = co.rerank(
        query=query, documents=documents_to_rerank, model="rerank-english-v2.0"
    )

    reranked_indices = [result.index for result in reranked_response]

    # Take the top 3 reranked results
    top_3_results = [results[i] for i in reranked_indices[:3]]

    return top_3_results


def frame_prompt(query: str, vector_results):
    # import ipdb;
    # ipdb.set_trace()
    # print(vector_results)

    # get the text from the results
    source_knowledge = "\n\n".join([f"{x.metadata['title']}\n{x.page_content}" for x in vector_results])

    # feed into an augmented prompt
    framed_prompt = f"""

    # THE USERS PREFERENCE'S ON THE CAR THEY ARE LOOKING FOR
    {query}

    # TOP 3 REVIEWS
    {source_knowledge}

    """
    return framed_prompt


def answer_question(question):
    vector_results = search_vectorstore(question)

    framed_prompt = frame_prompt(question, vector_results)

    template = """
    # MISSION
    You are a car expert named David who specalises in reviewing cars for DoneDeal Motors.
    A user will tell you the kind of car they are looking for and you will help them choose.

    # INSTRUCTIONS
    You will draw on your top 3 reviews to help inform the user's.
    You are from Dublin, Ireland and your super friendly and semi-formal.
    You will give the user 3 recomendations in the following format:

    # OUTPUT FORMAT
    Make Model

    Summary from the given context on why you are recommending this car.

    Make Model

    Summary from the given context on why you are recommending this car.

    Make Model

    Summary from the given context on why you are recommending this car.

    # RULES
    You should never make up information. Always use the context given to you.
    If the user mentions budget, you should take this into account when making your recomendations.
    """

    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    human_template = "{add_aug_prompt_here}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )

    result = chat(
        chat_prompt.format_prompt(
            add_aug_prompt_here=framed_prompt, text=""
        ).to_messages()
    )
    return [result.content, vector_results]
