"""
Resume Analysis Routes
This module defines the API endpoints for resume analysis.
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from pydantic import BaseModel
from typing import List, Optional
import PyPDF2
import docx
import io

from app.models.resume_analyzer import ResumeAnalyzer

# Initialize router
router = APIRouter(prefix="/analyze", tags=["Resume Analysis"])

# Initialize analyzer
analyzer = ResumeAnalyzer()

# Pydantic models for request/response
class ResumeTextRequest(BaseModel):
    text: str
    job_position: Optional[str] = None

class AnalysisResponse(BaseModel):
    skills: List[str]
    experiences: List[str]
    score: int
    feedback: str
    recommendations: List[str]

# Helper function to extract text from different file types
def extract_text_from_file(file: UploadFile) -> str:
    """
    Extract text content from uploaded file.
    
    Args:
        file (UploadFile): Uploaded file
        
    Returns:
        str: Extracted text content
    """
    try:
        if file.content_type == "text/plain":
            # Plain text file
            content = file.file.read()
            return content.decode("utf-8")
        elif file.content_type == "application/pdf":
            # PDF file
            pdf_reader = PyPDF2.PdfReader(file.file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        elif file.content_type in ["application/msword", 
                                  "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            # Word document
            doc = docx.Document(file.file)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting text from file: {str(e)}")

# API endpoint for analyzing resume text
@router.post("/text", response_model=AnalysisResponse)
async def analyze_resume_text(request: ResumeTextRequest):
    """
    Analyze resume text and return insights.
    
    Args:
        request (ResumeTextRequest): Request containing resume text and optional job position
        
    Returns:
        AnalysisResponse: Analysis results including skills, experiences, score, feedback, and recommendations
    """
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Resume text cannot be empty")
            
        # Perform analysis
        result = analyzer.analyze(request.text, request.job_position)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing resume: {str(e)}")

# API endpoint for analyzing uploaded resume file
@router.post("/file", response_model=AnalysisResponse)
async def analyze_resume_file(
    file: UploadFile = File(...),
    job_position: Optional[str] = Form(None)
):
    """
    Analyze uploaded resume file and return insights.
    
    Args:
        file (UploadFile): Uploaded resume file (txt, pdf, or docx)
        job_position (Optional[str]): Target job position for keyword matching
        
    Returns:
        AnalysisResponse: Analysis results including skills, experiences, score, feedback, and recommendations
    """
    try:
        if not file:
            raise HTTPException(status_code=400, detail="No file provided")
            
        # Extract text from file
        text = extract_text_from_file(file)
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from file or file is empty")
            
        # Perform analysis
        result = analyzer.analyze(text, job_position)
        return result
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing resume file: {str(e)}")