import shutil
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form, Body
from app.Utils.pinecone import get_answer, get_context, train_csv, train_pdf, train_txt, train_url, train_ms_word, delete_all_data, set_prompt, delete_data_by_metadata
from app.Models.ChatbotModel import add_page, add_file, remove_file, remove_page, add_new_chatbot, find_all_chatbots, remove_chatbot, find_chatbot_by_id, update_chatbot_by_id
from app.Models.ChatbotModel import ChatBotIdModel, User, AddNewBotModel, Chatbot, RequestPayload
from app.Utils.web_scraping import extract_content_from_url

from app.Utils.Auth import get_current_user
from fastapi.responses import StreamingResponse
from typing import Annotated
import os

router = APIRouter()


supported_file_extensions = [".csv", ".pdf", ".txt", ".doc", ".docx"]
current_bot = Chatbot()


@router.post("/add-new-chatbot")
async def add_new_chatbot_api(model: AddNewBotModel):
    # global current_bot

    # current_bot =
    try:
        return add_new_chatbot(email="aa@aa.com", botmodel=model)
        # return add_new_chatbot(email=user.email, botmodel=model)
    except Exception as e:
        raise e


@router.post("/find-all-chatbots")
def find_all_chatbots_api():
    try:
        return find_all_chatbots("aa@aa.com")
        # return find_all_chatbots(user.email)
    except Exception as e:
        raise e


@router.post("/find-chatbot-by-id")
def find_chatbot_by_id_api(id: ChatBotIdModel):
    global current_bot
    try:
        print("logid", id.log_id)
        current_bot = find_chatbot_by_id(id.id)
        print("sourceDis", current_bot.sourceDiscloser)
        update_chatbot_by_id(id.id, id.log_id)
        return current_bot
    except Exception as e:
        raise e


@router.post("/remove-chatbot")
def remove_chatbot_api(id: str = Form(...)):
    try:
        return remove_chatbot(id, "aa@aa.com")
        # return remove_chatbot(id, user.email)
    except Exception as e:
        raise e


@router.post("/find-pages-by-id")
def find_pages(id: str = Form(...)):
    try:
        print("id: ", id)
        result = find_chatbot_by_id(id)
        return result.pages
    except Exception as e:
        raise e


@router.post("/extract-content")
def add_new_chatbot_api(link: str = Form(...)):
    try:
        return extract_content_from_url(link)
    except Exception as e:
        raise e


@router.post("/add-page")
def add_page_api(id: str = Form(...), url: str = Form(...)):
    try:
        add_page(id, url)
        train_url(url, id)
        return True
    except Exception as e:
        raise e


@router.post("/add-training-file")
def add_training_file_api(file: UploadFile = File(...), bot_id: str = Form(...)):
    extension = os.path.splitext(file.filename)[1]
    if extension not in supported_file_extensions:
        raise HTTPException(
            status_code=500, detail="Invalid file type!")
    # print("valid filetype")
    try:
        # save file to server
        directory = "./train-data"
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(f"{directory}/{bot_id}-{file.filename}", "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # add training file
        if extension == ".csv":
            train_csv(file.filename, bot_id)
        elif extension == ".pdf":
            train_pdf(file.filename, bot_id)
        elif extension == ".txt":
            train_txt(file.filename, bot_id)
        elif extension == ".docx":
            train_ms_word(file.filename, bot_id)
        print("end-training")
        add_file(bot_id, file.filename)
    except Exception as e:
        print("training error")
        raise HTTPException(
            status_code=500, detail=e)


@router.post("/similar-context")
def find_similar_context(user: Annotated[User, Depends(get_current_user)], msg: str = Form(...), bot_id: str = Form(...)):
    print("msg: " + str(msg))
    if len(msg.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No Input Message",
        )
    return get_context(msg, bot_id, user.email, current_bot)


@router.post("/user-question")
def answer_to_user_question(request_payload: RequestPayload):
    print(request_payload.frequency_penalty)
    # current_bot = find_chatbot_by_id(bot_id)
    # global current_bot
    # print(current_bot.name, current_bot.language, current_bot.description," pass  ", current_bot.password)
    # return "hello, how can I assist you t?"
    get_context(request_payload.messages[-1]
                ['content'], request_payload.bot_Id)
    try:
        return StreamingResponse(get_answer(request_payload, "aa@aa.com"), media_type='text/event-stream')
    except Exception as e:
        raise e


@router.post("/clear-database")
def clear_database():
    delete_all_data()
    return True


@router.post("/clear-database-by-metadata")
def clear_database_by_metadata(filename: str = Form(...), id: str = Form(...), type: str = Form(...)):
    remove_file(id, filename) if type == "file" else remove_page(id, filename)
    delete_data_by_metadata(filename, id)


@router.post("/set-prompt")
def set_prompt_by_user(prompt: str = Form(...)):
    set_prompt(prompt)
