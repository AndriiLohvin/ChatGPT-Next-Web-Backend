import shutil
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form, Body
from app.Utils.pinecone import get_answer, get_context, train_csv, train_pdf, train_txt, train_url, train_ms_word, delete_all_data, set_prompt, delete_data_by_metadata
from app.Models.ChatbotModel import add_page, add_file, remove_file, remove_page, add_new_chatbot, find_all_chatbots, remove_chatbot, find_chatbot_by_id, update_chatbot_by_id
from app.Models.ChatbotModel import ChatBotIdModel, User, AddNewBotModel, Chatbot, RequestPayload
from app.Models.AnalyticsModel import ChatBotModel, count_total_chat_sessions, count_messages_per_session, count_messages_for_specific_period
from app.Utils.web_scraping import extract_content_from_url

from app.Utils.Auth import get_current_user
from fastapi.responses import StreamingResponse
from typing import Annotated
from datetime import datetime, timedelta
import os

router = APIRouter()


@router.post("/total_chat_sessions")
def total_chat_sessions(bot: ChatBotModel):
    try:
        return count_total_chat_sessions(bot.botId)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)


@router.post("/messages_per_session")
def messages_per_session(bot: ChatBotModel):
    count_messages_for_specific_period(timedelta(days=7))

    try:
        return {"message_per_session": count_messages_per_session(bot.botId),
                "weekly_message": count_messages_for_specific_period(timedelta(days=7)),
                "monthly_message": count_messages_for_specific_period(timedelta(days=30))}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
