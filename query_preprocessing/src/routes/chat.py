from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from ..security import get_current_user, UserBase
import requests
from ..guard_rails import RelevenceProompter
from ..query_manager import get_response
from ..types import (
    ApiQuery,
    QaQuery,
    QaResponse,
    Message,
    MessageRole,
    ChatThread,
)
from ..redis_manager import get_redis_manager
from ..chat_summary_manager import SummaryProompter
from ..create_llm import CreateLLM
import asyncio

router = APIRouter()

async def generator(response):
    print("*"*100)
    print(response)
    print("*"*100)
    for chunk in response.split():
        yield f"{chunk} "
        await asyncio.sleep(0.1)


@router.post("/generate")
async def get_ai_message(
    query: ApiQuery, current_user: UserBase = Depends(get_current_user)
):
    llm = CreateLLM(query.model, query.embeddings_model).getModel()

    chat_manager = get_redis_manager(current_user.user_id)
    if not chat_manager.has_thread(query.thread_id):
        chat_manager.add_thread(ChatThread(id=query.thread_id, title=query.prompt))
    chat_history = chat_manager.get_chat(query.thread_id)

    chat_manager.add_message(
        query.thread_id, Message(role=MessageRole.user, content=query.prompt)
    )

    try:
        summarizer = SummaryProompter()
        summary = summarizer.get_summary(llm, chat_history)

        qa_query = QaQuery(**(query.dict() | {"summary": summary}))
        relevance = RelevenceProompter()
        guard_chain = relevance.relevance_chain(llm)
        resp = guard_chain.invoke(qa_query.dict())
        if not resp.is_related():
            resp = QaResponse(
                **{
                    "type": QaResponse.Type.REJECTED,
                    "response": resp.reason,
                }
            )

            chat_manager.add_message(
                query.thread_id,
                Message(role=MessageRole.assistant, content=resp.response),
            )

            return StreamingResponse(generator(resp), media_type="text/event-stream")

        response = get_response(qa_query)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=418, detail=str(e))
    else:
        chat_manager.add_message(
            query.thread_id,
            Message(role=MessageRole.assistant, content=response["response"]),
        )
        return StreamingResponse(generator(response['response']), media_type="text/event-stream")



