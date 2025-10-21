# AI Resume Analyzer

An intelligent web service that automatically analyzes resumes using Natural Language Processing (NLP) to provide actionable insights, scores, and improvement recommendations.

## Features

- **Skill Extraction**: Automatically identifies technical skills and competencies from resumes
- **Experience Analysis**: Extracts key experience highlights and accomplishments
- **Scoring System**: Provides an overall score (0-100) based on resume quality metrics
- **Personalized Feedback**: Offers tailored feedback on resume strengths and weaknesses
- **Job-Specific Recommendations**: Provides targeted suggestions based on desired job positions
- **Multiple Input Formats**: Supports plain text, PDF, and DOC/DOCX file uploads
- **RESTful API**: Exposes endpoints for integration with other applications

## Technologies Used

- **FastAPI**: High-performance web framework for building APIs with Python
- **Hugging Face Transformers**: State-of-the-art NLP models for Named Entity Recognition
- **spaCy**: Industrial-strength Natural Language Processing library
- **PyPDF2**: PDF text extraction capabilities
- **python-docx**: Microsoft Word document processing
- **Pydantic**: Data validation and settings management

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/alhm002/ai-resume-analyzer.git
   cd ai-resume-analyzer
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install spaCy language model:
   ```bash
   python -m spacy download en_core_web_sm
   ```

## Usage

1. Start the server:
   ```bash
   python main.py
   ```

2. Access the web interface at `http://localhost:8000`

3. Use the API endpoints:
   - `POST /api/v1/analyze/text` - Analyze resume text
   - `POST /api/v1/analyze/file` - Analyze uploaded resume file
   - `GET /health` - Health check endpoint

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Example Request

### Analyze Resume Text
```json
POST /api/v1/analyze/text
{
  "text": "Your resume text here...",
  "job_position": "software-engineer"
}
```

### Analyze Resume File
```bash
curl -X POST "http://localhost:8000/api/v1/analyze/file" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@resume.pdf" \
  -F "job_position=software-engineer"
```

## Response Format

```json
{
  "skills": ["Python", "JavaScript", "React"],
  "experiences": ["Developed web applications using React", "Led a team of 5 developers"],
  "score": 85,
  "feedback": "Excellent resume! Well-structured and comprehensive.",
  "recommendations": [
    "Add more technical skills and certifications relevant to your field.",
    "Include more quantifiable achievements with specific metrics."
  ]
}
```

## Project Structure

```
ai-resume-analyzer/
├── app/
│   ├── models/
│   │   └── resume_analyzer.py    # Core NLP logic
│   └── routes/
│       └── resume_analysis.py    # API endpoints
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Hugging Face](https://huggingface.co/) for providing excellent NLP models
- [spaCy](https://spacy.io/) for powerful text processing capabilities
- [FastAPI](https://fastapi.tiangolo.com/) for the high-performance web framework