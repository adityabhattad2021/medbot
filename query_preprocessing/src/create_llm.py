from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.embeddings import OllamaEmbeddings
import os
from dotenv import load_dotenv, find_dotenv
from langchain_community.llms import Ollama

from langchain_groq import ChatGroq
from langchain_anthropic import ChatAnthropic

from .types import Model, EmbeddingsModel

load_dotenv(find_dotenv())


class CreateLLM:
 
    @staticmethod
    def getModel(model: Model, temp=0):
        match model:
            case Model.gemini_pro:
                llm = GoogleGenerativeAI(
                    model=model.model(), google_api_key=os.getenv("GOOGLE_API_KEY")
                )
            case Model.gemini_pro_chat:
                llm = ChatGoogleGenerativeAI(
                    model=model.model(),
                    temperature=temp,
                    convert_system_message_to_human=True,
                    google_api_key=os.getenv("GOOGLE_API_KEY"),
                )
            case Model.ollama_llama2 | Model.ollama_llama2_uncensored:
                llm = Ollama(
                    base_url=os.getenv("OLLAMA_URL"),
                    model=model.model() + ":vram-34",
                    temperature=temp,
                )
            case Model.groq_mistral_8x7b | Model.groq_llama2_70b | Model.groq_gemma_7b:
                llm = ChatGroq(
                    model_name=model.model(),
                    temperature=temp,
                    groq_api_key=os.getenv("GROQ_API_KEY"),
                )
            case Model.claude_3_opus:
                llm = ChatAnthropic(
                    model_name=model.model(),
                    temperature=temp,
                    anthropic_api_key=os.getenv("CLAUDE_API_KEY"),
                )
            case _:
                raise RuntimeError(message="Wrong llm name")
        return llm

    @staticmethod
    def get_embeddings(embeddings_model: EmbeddingsModel):
        match embeddings_model:
            case EmbeddingsModel.gemini_pro:
                embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
            case EmbeddingsModel.ollama_llama2 | EmbeddingsModel.ollama_llama2_uncensored:
                embeddings = OllamaEmbeddings(model=embeddings_model.model() + ":vram-34")
            case _:
                raise RuntimeError("unknown embedding model")
        return embeddings
