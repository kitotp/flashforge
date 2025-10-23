from fastapi import FastAPI , File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from typing import Iterator, List
from openai import OpenAI
from io import BytesIO

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

async def read_pdf_pages(file: UploadFile, max_pages: int = 10, max_chars_per_page: int | None = 12000) -> List[str]:
    if not file:
        return {"message": "No upload file sent"}
    
    data = await file.read()
    reader = PdfReader(BytesIO(data))
    pages_text: List[str] = []
    
    total = min(len(reader.pages), max_pages)
    for i in range(total):
        text = (reader.pages[i].extract_text() or "").strip()

        if max_chars_per_page < len(text):
            text = text[:max_chars_per_page]
        
        pages_text.append(text)
    return pages_text

def stream_page(text: str, page_idx: int ) -> Iterator[str]:

    yield f"event: page\ndata: {page_idx}\n\n"
    
    if not text:
        yield f"data: (page {page_idx} has no data)"
        return

    with client.responses.stream(
        model="gpt-4o-mini",
        input = text,
        instructions=f"Make 3 concise questions about page {page_idx} of the document.",
    ) as stream:
        for event in stream:
            if event.type=="response.output_text.delta":
                yield f"data: {event.delta}\n\n"
            elif event.type=="response.completed":
                yield f"event: done\n data: [DONE]\n\n"
    
def stream_all_pages(pages_text: List[str]):
    try:
        for idx, txt in enumerate(pages_text, start = 1):
            yield from stream_page(txt, idx)
        yield "event: done\ndata: [DONE]\n\n"
    except Exception as e:
        yield f"event: error\ndata: error streaming all pages\n\n"
        yield "event: done\ndata: [DONE]\n\n"
 

@app.post("/analize")
async def analize(file: UploadFile | None = None, limit = 10, max_chars = 12000):
    pages_text = await read_pdf_pages(file, max_pages = limit , max_chars_per_page = max_chars)
    

    return StreamingResponse(
        stream_all_pages(pages_text),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )

