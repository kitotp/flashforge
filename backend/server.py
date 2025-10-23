from fastapi import FastAPI , File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os
from os.path import join, dirname
from dotenv import load_dotenv
from pypdf import PdfReader
from fastapi.responses import StreamingResponse

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key = OPENAI_API_KEY)




app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/submitForm")
async def root():
    return {"message": "Form submitted"}


@app.post("/analize")
async def analize(file: UploadFile | None = None):
    if not file:
        return {"message": "No upload file sent"}
    
    reader = PdfReader(file.file)
    first_page = reader.pages[0]
    text = first_page.extract_text() or ""
    


    def gen():
        headers = []
        with client.responses.create(
            model="gpt-4o",
            input = text,
            instructions="Make 10 questions from the following text.",
            stream=True
        ) as stream:
            for event in stream:
                if event.type=="response.output_text.delta":
                    yield f"data: {event.delta}\n\n"
                elif event.type=="response.completed":
                    yield f"event: done\n data: [DONE]\n\n"
    

    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )

