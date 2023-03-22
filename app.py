# from fastapi import FastAPI, Request
# from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates
# from info import FolderInfo
# from question_intaker import clean_question, ask_question

# app = FastAPI()
# templates = Jinja2Templates(directory="templates/")
# path_to_index_file = "templates/index.html"

# folder_info = FolderInfo.load_from_msgpack(path_to_index_file)


# @app.get("/")
# async def index(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})


# @app.post("/question")
# async def question(request: Request, question: str):
#     cleaned_question = clean_question(question)
#     answer = ask_question(cleaned_question, folder_info)
#     return {"answer": answer}


# @app.get("/question")
# async def question(request: Request, question: str):
#     cleaned_question = clean_question(question)
#     answer = ask_question(cleaned_question, folder_info)
#     return {"answer": answer}

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from info import FolderInfo
from question_intaker import clean_question, ask_question

app = FastAPI()
templates = Jinja2Templates(directory="templates/")
path_to_index_file = "outputs/03_22_12_29_32.msgpack"

folder_info = FolderInfo.load_from_msgpack(path_to_index_file)


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/question")
async def question(request: Request, question: str = Form(...)):
    cleaned_question = clean_question(question)
    question_answer, auto_gen_context_feedback, auto_gen_answer_feedback = ask_question(
        cleaned_question, folder_info
    )
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "question": cleaned_question,
            "answer": question_answer,
            "context_feedback": auto_gen_context_feedback,
            "answer_feedback": auto_gen_answer_feedback,
        },
    )


@app.post("/feedback")
async def feedback(
    request: Request,
    question: str = Form(...),
    answer: str = Form(...),
    context_feedback: int = Form(...),
    answer_feedback: int = Form(...),
):
    # TODO: Handle feedback data
    return RedirectResponse(url="/")
