#Actionableitems , decision , questions 

from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
import os 


def get_llm():
    return ChatMistralAI(model = "mistral-small-latest", mistral_api_key = os.getenv("MISTRAL_API_KEY"),temperature=0.2)



def build_chain(system_prompt : str):
    llm = get_llm()
    return (
        RunnablePassthrough() | RunnableLambda(lambda x : {"text" : x}) |ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human","{text}"),
    ]) | llm |StrOutputParser()
    )

def extract_action_items(transcript:str)->str:
    chain = build_chain(
         "You are an expert meeting analyst. From the meeting transcript, "
        "extract all action items. For each provide:\n"
        "- Task description\n"
        "- Owner (who is responsible)\n"
        "- Deadline (if mentioned, else write 'Not specified')\n\n"
        "Format as a numbered list. If none found say 'No action items found.'"
    )

    return chain.invoke(transcript)


def extract_key_decisions(transcript: str) -> str:
    chain = build_chain(
        "You are an expert meeting analyst. From the meeting transcript, "
        "extract all key decisions made. Format as a numbered list. "
        "If none found say 'No key decisions found.'"
    )
    return chain.invoke(transcript)


def extract_questions(transcript: str) -> str:
    chain = build_chain(
        "From the meeting transcript, extract all unresolved questions "
        "or topics needing follow-up. Format as a numbered list. "
        "If none found say 'No open questions found.'"
    )
    return chain.invoke(transcript)


def extract_timestamped_topics(transcript: str, duration_sec: float = 0) -> str:
    duration_prompt = ""
    if duration_sec > 0:
        m = int(duration_sec // 60)
        s = int(duration_sec % 60)
        max_ts = f"{m:02d}:{s:02d}"
        duration_prompt = (
            f" CRITICAL CONSTRAINT: The total audio/video length is EXACTLY {max_ts} ({int(duration_sec)} seconds). "
            f"ALL timestamps MUST stay strictly within [00:00] to [{max_ts}]. "
            f"Under NO circumstances should any timestamp exceed [{max_ts}]."
        )

    chain = build_chain(
        "From the meeting transcript, extract a chronological outline of key topics discussed with "
        f"accurate timestamp ranges.{duration_prompt} Format as a clean bulleted list."
    )
    return chain.invoke(transcript)