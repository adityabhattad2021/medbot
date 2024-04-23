from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import (
    RunnableParallel,
    RunnableLambda,
)
from langchain_core.runnables.base import RunnableEach
from langchain.vectorstores.pgvector import PGVector

from langchain_community.tools.pubmed.tool import PubmedQueryRun
from langchain.retrievers.tavily_search_api import TavilySearchAPIRetriever, SearchDepth
import google.generativeai as genai
import os
from typing import List
from functools import lru_cache
from dotenv import find_dotenv, load_dotenv
from .types import Model, QaQuery, Strategy, EmbeddingsModel
from .llm_manager import LlmManager
from .proompter import Proompter, printer
from .proompts import pubmed_query_prompt_template

load_dotenv(find_dotenv())
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


class VectorDbQaService(Proompter):
    def qa_chain(self, llm, embeddings):
        db = PGVector(
            collection_name=os.getenv("CONNECTION_NAME"),
            connection_string=os.getenv("CONNECTION_STRING"),
            embedding_function=embeddings,
        )

        return (
            printer
            | RunnableParallel(
                prompt=self.question_rephrase_chain(llm),
                summary=lambda x: x["summary"],
            )
            | printer
            | RunnableParallel(
                prompt=lambda x: x["prompt"],
                summary=lambda x: x["summary"],
                context=lambda x: db.as_retriever().invoke(x["prompt"]),
            )
            | printer
            | RunnableParallel(
                response=self.medical_chatbot_prompt_chain(llm),
                context=lambda x: x["context"],
            )
            | printer
        )


class PubmedQaService(Proompter):
    def genrate_search_queries_chain(self, llm):
        return (
            RunnableParallel(
                questions=(
                    # search_query_prompt_template
                    pubmed_query_prompt_template
                    | printer
                    | llm
                    | StrOutputParser()
                    | printer
                    | self.hacky_list_of_strings_chain()
                ),
                prompt=lambda x: x["prompt"],
            )
            | printer
            # | RunnableLambda(lambda x: [x["prompt"]] + x["questions"])
            | RunnableLambda(lambda x: x["questions"])
            | printer
        )

    def pubmed_context_chain(self, llm):
        return self.genrate_search_queries_chain(llm) | RunnableEach(
            bound=(
                RunnableParallel(
                    prompt=lambda x: x,
                    context=lambda x: Document(page_content=PubmedQueryRun().invoke(x)),
                )
            )
        )

    def qa_chain(self, llm, embeddings):
        return (
            printer
            | RunnableParallel(
                prompt=self.question_rephrase_chain(llm),
                summary=lambda x: x["summary"],
            )
            | printer
            | RunnableParallel(
                prompt=lambda x: x["prompt"],
                summary=lambda x: x["summary"],
                context=self.pubmed_context_chain(llm),
            )
            | printer
            | RunnableParallel(
                response=self.medical_chatbot_prompt_chain(llm),
                context=lambda x: x["context"],
            )
            | printer
        )


class TavilyQaService(Proompter):
    def tavily_chain(self):
        return TavilySearchAPIRetriever(
            k=1,
            api_key=os.getenv("TAVILY_AI_API_KEY"),
            search_depth=SearchDepth.ADVANCED,
            include_generated_answer=True,
        )

    def web_context_chain(self, llm, embeddings):
        return (
            self.generate_search_queries_chain(llm)
            | RunnableEach(
                bound=(
                    RunnableParallel(
                        prompt=lambda x: x,
                        urls=self.tavily_chain(),
                    )
                )
            )
            | printer
            | RunnableLambda(lambda x: [d for d in x])
            | printer
        )

    def qa_chain(self, llm, embeddings):
        return (
            RunnableParallel(
                prompt=self.question_rephrase_chain(llm),
                summary=lambda x: x["summary"],
            )
            | printer
            | RunnableParallel(
                prompt=lambda x: x["prompt"],
                summary=lambda x: x["summary"],
                context=self.web_context_chain(llm, embeddings),
            )
            | printer
            | RunnableParallel(
                context=lambda x: x["context"],
                response=self.generic_chatbot_prompt_chain(llm),
            )
        )



@lru_cache
def get_response(query: QaQuery) -> str:
    llm = LlmManager.getModel(query.model)
    embeddings = LlmManager.get_embeddings(query.embeddings_model)

    match query.strategy:
        case Strategy.medical_database:
            strategy = VectorDbQaService()
        case Strategy.pubmed_search:
            strategy = PubmedQaService()
        case Strategy.web_search_api:
            strategy = TavilyQaService()
        case _:
            raise RuntimeError("unimplemented strategy")

    chain = strategy.qa_chain(llm, embeddings)
    res = chain.invoke(query.dict())
    return res


if __name__ == "__main__":
    query = QaQuery(
        **{
            "model": Model.groq_mistral_8x7b,
            "embeddings_model": EmbeddingsModel.gemini_pro,
            "strategy": Strategy.web_search_api,
            "prompt": "what medicines do i take for headache?",
            "summary": "None",
        }
    )
    resp = get_response(query)
