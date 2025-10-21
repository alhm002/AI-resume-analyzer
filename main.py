from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
import os

from app.routes import resume_analysis

# Initialize FastAPI app
app = FastAPI(
    title="AI Resume Analyzer",
    description="A web service that automatically analyzes resumes using Natural Language Processing (NLP)",
    version="1.0.0"
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(resume_analysis.router, prefix="/api/v1")

# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint to verify the service is running.
    Returns "OK" if the service is up and running.
    """
    return {"status": "OK"}

# Serve the frontend
@app.get("/", response_class=HTMLResponse, tags=["Frontend"])
def read_root():
    """
    Serve the main frontend page for uploading resumes.
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Resume Analyzer</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #2c3e50;
                text-align: center;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }
            textarea, input[type="file"], select {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 16px;
                box-sizing: border-box;
            }
            textarea {
                height: 200px;
                resize: vertical;
            }
            button {
                background-color: #3498db;
                color: white;
                padding: 12px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                width: 100%;
            }
            button:hover {
                background-color: #2980b9;
            }
            #result {
                margin-top: 20px;
                padding: 15px;
                border-radius: 5px;
                display: none;
            }
            .success {
                background-color: #d4edda;
                border: 1px solid #c3e6cb;
                color: #155724;
            }
            .error {
                background-color: #f8d7da;
                border: 1px solid #f5c6cb;
                color: #721c24;
            }
            .loading {
                text-align: center;
                display: none;
            }
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #3498db;
                border-radius: 50%;
                width: 30px;
                height: 30px;
                animation: spin 2s linear infinite;
                margin: 0 auto;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>AI Resume Analyzer</h1>
            <p>Upload your resume or paste the text to get AI-powered analysis and improvement suggestions.</p>
            
            <form id="resumeForm">
                <div class="form-group">
                    <label for="jobPosition">Target Job Position (Optional):</label>
                    <select id="jobPosition">
                        <option value="">Select a position (optional)</option>
                        <option value="software-engineer">Software Engineer</option>
                        <option value="data-scientist">Data Scientist</option>
                        <option value="product-manager">Product Manager</option>
                        <option value="web-developer">Web Developer</option>
                        <option value="ui-ux-designer">UI/UX Designer</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="resumeText">Resume Text:</label>
                    <textarea id="resumeText" placeholder="Paste your resume text here..."></textarea>
                </div>
                
                <div class="form-group">
                    <label for="resumeFile">Or Upload Resume File:</label>
                    <input type="file" id="resumeFile" accept=".txt,.pdf,.doc,.docx">
                </div>
                
                <button type="submit">Analyze Resume</button>
            </form>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Analyzing your resume... This may take a few moments.</p>
            </div>
            
            <div id="result"></div>
        </div>

        <script>
            document.getElementById('resumeForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const resumeText = document.getElementById('resumeText').value;
                const resumeFile = document.getElementById('resumeFile').files[0];
                const jobPosition = document.getElementById('jobPosition').value;
                
                // Show loading indicator
                document.getElementById('loading').style.display = 'block';
                document.getElementById('result').style.display = 'none';
                
                try {
                    let response;
                    
                    if (resumeFile) {
                        // Handle file upload
                        const formData = new FormData();
                        formData.append('file', resumeFile);
                        if (jobPosition) {
                            formData.append('job_position', jobPosition);
                        }
                        
                        response = await fetch('/api/v1/analyze/file', {
                            method: 'POST',
                            body: formData
                        });
                    } else if (resumeText) {
                        // Handle text input
                        const requestData = {
                            text: resumeText
                        };
                        if (jobPosition) {
                            requestData.job_position = jobPosition;
                        }
                        
                        response = await fetch('/api/v1/analyze/text', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify(requestData)
                        });
                    } else {
                        throw new Error('Please provide either resume text or a file');
                    }
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        displayResult(result, 'success');
                    } else {
                        displayResult(result.detail || 'An error occurred during analysis', 'error');
                    }
                } catch (error) {
                    displayResult(error.message || 'An error occurred during analysis', 'error');
                } finally {
                    // Hide loading indicator
                    document.getElementById('loading').style.display = 'none';
                }
            });
            
            function displayResult(data, type) {
                const resultDiv = document.getElementById('result');
                resultDiv.className = type;
                resultDiv.style.display = 'block';
                
                if (type === 'success') {
                    resultDiv.innerHTML = `
                        <h3>Analysis Results</h3>
                        <p><strong>Overall Score:</strong> ${data.score}/100</p>
                        
                        <h4>Extracted Skills:</h4>
                        <ul>
                            ${data.skills.map(skill => `<li>${skill}</li>`).join('')}
                        </ul>
                        
                        <h4>Experience Highlights:</h4>
                        <ul>
                            ${data.experiences.map(exp => `<li>${exp}</li>`).join('')}
                        </ul>
                        
                        <h4>Feedback:</h4>
                        <p>${data.feedback}</p>
                        
                        <h4>Recommendations:</h4>
                        <ul>
                            ${data.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                        </ul>
                    `;
                } else {
                    resultDiv.innerHTML = `<p>Error: ${data}</p>`;
                }
            }
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)