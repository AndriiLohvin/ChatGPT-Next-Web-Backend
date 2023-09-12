from pydantic import BaseModel
from datetime import datetime, timedelta
from app.Models.ChatbotModel import ChatbotsDB
from app.Models.ChatLogModel import ChatlogsDB


class ChatBotModel(BaseModel):
    botId: str


def count_total_chat_sessions(botId: str):
    print(ChatlogsDB.count_documents({"botId": botId}))
    return ChatlogsDB.count_documents({"botId": botId})


def count_messages_per_session(botId: str):
    print("botid: ", botId)
    results = ChatlogsDB.find({"botId": botId}, {"messages": 1})
    session_count = 0
    message_size = 0
    for result in results:
        session_count += 1
        message_size += len(result["messages"])
    # print(session_count)
    # print(message_size)
    return format(message_size/session_count, '.2f')


def count_messages_for_specific_period(duration: timedelta):
    threshold = datetime.now() - duration
    # print(datetime.now())
    # print(week_ago)
    return ChatlogsDB.count_documents({"createdDate": {"$gt": threshold}})
