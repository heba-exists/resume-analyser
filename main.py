import io
import httpx
from fastapi import FastAPI, UploadFile, File, Request, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def verify_session(request: Request):
    cookies = request.cookies
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://127.0.0.1:5000/verify-session",
            cookies=cookies
        )
    if response.status_code != 200 or not response.json().get("valid"):
        raise HTTPException(status_code=401, detail="Not logged in")
    return response.json()


SKILL_KEYWORDS = [
    "python", "java", "javascript", "react", "node.js", "sql",
    "machine learning", "fastapi", "django", "flask", "aws", "docker",
    "git", "html", "css", "mongodb", "c++", "typescript", "kubernetes",
    "rest api", "graphql", "pandas", "numpy", "tensorflow", "pytorch"
]


def extract_skills(text: str):
    text_lower = text.lower()
    found_skills = [skill for skill in SKILL_KEYWORDS if skill in text_lower]
    return found_skills


@app.get("/")
def home():
    return {"message": "Resume Analyzer API is working!"}


@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...), user=Depends(verify_session)):
    try:
        if file.content_type != "application/pdf":
            return {"error": "Only PDF files are allowed."}

        contents = await file.read()

        if len(contents) > 5 * 1024 * 1024:
            return {"error": "File too large. Max 5MB."}

        pdf_stream = io.BytesIO(contents)
        reader = PdfReader(pdf_stream)

        extracted_text = ""
        for page in reader.pages:
            extracted_text += page.extract_text() or ""

        return {
            "filename": file.filename,
            "file_size": len(contents),
            "message": "Resume received and text extracted successfully!",
            "extracted_text": extracted_text
        }

    except Exception as e:
        return {"error": str(e)}


@app.post("/analyze-resume")
async def analyze_resume(
    file: UploadFile = File(...),
    job_description: str = Form(...),
    user=Depends(verify_session)
):
    try:
        if file.content_type != "application/pdf":
            return {"error": "Only PDF files are allowed."}

        contents = await file.read()

        if len(contents) > 5 * 1024 * 1024:
            return {"error": "File too large. Max 5MB."}

        pdf_stream = io.BytesIO(contents)
        reader = PdfReader(pdf_stream)

        extracted_text = ""
        for page in reader.pages:
            extracted_text += page.extract_text() or ""

        resume_skills = set(extract_skills(extracted_text))
        job_skills = set(extract_skills(job_description))

        matched = list(resume_skills & job_skills)
        missing = list(job_skills - resume_skills)

        return {
            "matched_skills": matched,
            "missing_skills": missing,
            "match_percentage": round(len(matched) / len(job_skills) * 100, 1) if job_skills else 0
        }

    except Exception as e:
        return {"error": str(e)}