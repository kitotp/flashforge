from fastapi import FastAPI , File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os
from os.path import join, dirname
from dotenv import load_dotenv
from pypdf import PdfReader

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key = OPENAI_API_KEY)

"""
response = client.responses.create(
    model="gpt-4o",
    input = [
        {
            "role": "user",
            "content": [
                {
                    "type": "input_file",
                    "file_id": file.id,
                },
                {
                    "type": "input_text",
                    "text": "Divide this conspect into 10 questions.",
                },
            ]
        }
    ]
)
"""

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
    
    try:
        reader = PdfReader(file.file)
        first_page = reader.pages[0]
        text = first_page.extract_text() or ""

        return {
            "filename": file.filename,
            "first_page_text": text,
            "pages": len(reader.pages),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read PDF: {e}")


    


    

    print(file)

