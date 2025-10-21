"""
Resume Analyzer Model
This module contains the core logic for analyzing resumes using NLP techniques.
"""

from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
from transformers.pipelines import Pipeline
from typing import List, Dict, Tuple, Optional, Any
import re
import spacy
from collections import Counter

class ResumeAnalyzer:
    def __init__(self):
        """
        Initialize the ResumeAnalyzer with necessary NLP models.
        """
        try:
            # Load spaCy model for preprocessing (optional)
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # If spaCy model is not available, continue without it
            self.nlp = None
            print("Warning: spaCy model not found. Some features may be limited.")
        
        # Initialize Hugging Face transformers pipeline for NER
        try:
            self.tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
            self.model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")
            self.ner_pipeline: Optional[Pipeline] = pipeline("ner", 
                                       model=self.model, 
                                       tokenizer=self.tokenizer,
                                       aggregation_strategy="simple")
        except Exception as e:
            print(f"Warning: Could not load BERT NER model. Error: {e}")
            self.ner_pipeline = None
        
        # Define skill keywords for matching
        self.skill_keywords = [
            # Programming languages
            "python", "java", "javascript", "c++", "c#", "ruby", "php", "swift", "kotlin", "go", "rust",
            "scala", "r", "matlab", "sql", "typescript", "perl", "shell", "bash",
            
            # Web technologies
            "html", "css", "react", "angular", "vue", "node.js", "express", "django", "flask",
            "spring", "asp.net", "laravel", "rails", "bootstrap", "jquery", "ajax",
            
            # Databases
            "mysql", "postgresql", "mongodb", "redis", "oracle", "sql server", "firebase",
            "cassandra", "elasticsearch", "dynamodb",
            
            # Cloud platforms
            "aws", "azure", "google cloud", "gcp", "docker", "kubernetes", "terraform",
            "jenkins", "ansible", "chef", "puppet",
            
            # Data science & ML
            "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras",
            "matplotlib", "seaborn", "plotly", "nltk", "spacy", "opencv",
            "hadoop", "spark", "hive", "kafka", "airflow",
            
            # Other technologies
            "git", "linux", "unix", "ubuntu", "centos", "agile", "scrum", "jira",
            "confluence", "excel", "tableau", "power bi", "sap", "erp"
        ]
        
        # Job position keywords for matching
        self.job_keywords = {
            "software-engineer": [
                "programming", "coding", "software development", "debugging", "testing",
                "algorithms", "data structures", "oop", "object oriented", "design patterns",
                "version control", "git", "api", "rest", "microservices"
            ],
            "data-scientist": [
                "machine learning", "deep learning", "neural networks", "regression",
                "classification", "clustering", "nlp", "natural language processing",
                "statistical analysis", "data visualization", "pandas", "numpy", "r",
                "python", "tensorflow", "pytorch", "scikit-learn"
            ],
            "web-developer": [
                "html", "css", "javascript", "react", "angular", "vue", "node.js",
                "frontend", "backend", "responsive design", "cross-browser compatibility",
                "rest api", "json", "ajax", "bootstrap", "jquery"
            ],
            "product-manager": [
                "product strategy", "roadmap", "market research", "user stories",
                "agile", "scrum", "sprint", "product lifecycle", "ux", "ui",
                "stakeholder management", "prioritization", "metrics", "kpi"
            ],
            "ui-ux-designer": [
                "user experience", "user interface", "wireframing", "prototyping",
                "figma", "sketch", "adobe xd", "usability testing", "accessibility",
                "design thinking", "user research", "information architecture",
                "visual design", "typography", "color theory"
            ]
        }

    def preprocess_text(self, text: str) -> str:
        """
        Preprocess the resume text using spaCy (if available).
        
        Args:
            text (str): Raw resume text
            
        Returns:
            str: Preprocessed text
        """
        if self.nlp:
            doc = self.nlp(text)
            # Remove stop words and punctuation, lemmatize
            tokens = [token.lemma_.lower() for token in doc 
                     if not token.is_stop and not token.is_punct and token.is_alpha]
            return " ".join(tokens)
        else:
            # Basic preprocessing if spaCy is not available
            text = text.lower()
            # Remove extra whitespaces
            text = re.sub(r'\s+', ' ', text)
            return text.strip()

    def extract_skills(self, text: str) -> List[str]:
        """
        Extract skills and technologies from the resume text.
        
        Args:
            text (str): Resume text
            
        Returns:
            List[str]: List of extracted skills
        """
        # Preprocess text
        processed_text = self.preprocess_text(text).lower()
        
        # Find skills using keyword matching
        found_skills = []
        for skill in self.skill_keywords:
            if skill.lower() in processed_text:
                found_skills.append(skill.title())
        
        # Use NER to extract organizations, persons, and locations
        if self.ner_pipeline:
            try:
                ner_results = self.ner_pipeline(text)
                # Extract organizations as potential skills/experiences
                org_entities = [entity['word'] for entity in ner_results 
                               if entity['entity_group'] == 'ORG']
                found_skills.extend(org_entities)
            except Exception as e:
                print(f"NER extraction failed: {e}")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_skills = []
        for skill in found_skills:
            if skill not in seen:
                seen.add(skill)
                unique_skills.append(skill)
        
        return unique_skills[:20]  # Return top 20 skills

    def extract_experiences(self, text: str) -> List[str]:
        """
        Extract experience highlights from the resume text.
        
        Args:
            text (str): Resume text
            
        Returns:
            List[str]: List of experience highlights
        """
        # Split text into lines
        lines = text.split('\n')
        
        # Look for lines that start with action verbs (indicative of experience descriptions)
        action_verbs = [
            "managed", "developed", "created", "implemented", "designed", "optimized",
            "led", "collaborated", "analyzed", "improved", "increased", "reduced",
            "streamlined", "automated", "mentored", "trained", "coordinated"
        ]
        
        experiences = []
        for line in lines:
            line_clean = line.strip().lower()
            # Check if line starts with an action verb and has some substance
            if len(line_clean) > 10 and any(verb in line_clean for verb in action_verbs):
                # Capitalize first letter
                formatted_line = line.strip()
                if formatted_line:
                    formatted_line = formatted_line[0].upper() + formatted_line[1:]
                    experiences.append(formatted_line)
        
        # Limit to top 10 experiences
        return experiences[:10]

    def calculate_score(self, text: str, skills: List[str], experiences: List[str]) -> int:
        """
        Calculate an overall score for the resume based on various factors.
        
        Args:
            text (str): Resume text
            skills (List[str]): Extracted skills
            experiences (List[str]): Extracted experiences
            
        Returns:
            int: Score out of 100
        """
        score = 0
        
        # Length scoring (optimal resume length is typically 1-2 pages)
        word_count = len(text.split())
        if 200 <= word_count <= 800:
            score += 30
        elif word_count > 100:
            score += 20
        else:
            score += 10
            
        # Skills diversity scoring
        if len(skills) >= 10:
            score += 25
        elif len(skills) >= 5:
            score += 15
        else:
            score += 5
            
        # Experience depth scoring
        if len(experiences) >= 5:
            score += 25
        elif len(experiences) >= 2:
            score += 15
        else:
            score += 5
            
        # Keyword density scoring
        keyword_count = sum(1 for keyword in self.skill_keywords 
                           if keyword.lower() in text.lower())
        if keyword_count >= 15:
            score += 20
        elif keyword_count >= 8:
            score += 10
        else:
            score += 5
            
        # Ensure score is between 0 and 100
        return min(max(score, 0), 100)

    def generate_feedback(self, text: str, skills: List[str], experiences: List[str], score: int) -> str:
        """
        Generate feedback about the resume based on analysis.
        
        Args:
            text (str): Resume text
            skills (List[str]): Extracted skills
            experiences (List[str]): Extracted experiences
            score (int): Overall score
            
        Returns:
            str: Feedback message
        """
        feedback_parts = []
        
        if score >= 80:
            feedback_parts.append("Excellent resume! Well-structured and comprehensive.")
        elif score >= 60:
            feedback_parts.append("Good resume with some room for improvement.")
        elif score >= 40:
            feedback_parts.append("Fair resume, but needs significant improvements.")
        else:
            feedback_parts.append("Needs substantial improvements to be competitive.")
            
        # Length feedback
        word_count = len(text.split())
        if word_count < 150:
            feedback_parts.append("Consider adding more content to showcase your experience.")
        elif word_count > 1000:
            feedback_parts.append("Consider shortening your resume to make it more concise.")
            
        # Skills feedback
        if len(skills) < 5:
            feedback_parts.append("Try to highlight more technical skills relevant to your field.")
            
        # Experience feedback
        if len(experiences) < 3:
            feedback_parts.append("Include more specific examples of your achievements with metrics.")
            
        # Keyword feedback
        if "summary" not in text.lower() and "objective" not in text.lower():
            feedback_parts.append("Consider adding a professional summary or objective.")
            
        if "@" not in text and "email" not in text.lower():
            feedback_parts.append("Make sure your contact information is clearly visible.")
            
        return " ".join(feedback_parts)

    def generate_recommendations(self, text: str, skills: List[str], 
                               experiences: List[str], job_position: Optional[str] = None) -> List[str]:
        """
        Generate recommendations for improving the resume.
        
        Args:
            text (str): Resume text
            skills (List[str]): Extracted skills
            experiences (List[str]): Extracted experiences
            job_position (Optional[str]): Target job position
            
        Returns:
            List[str]: List of recommendations
        """
        recommendations = []
        
        # General recommendations
        if len(skills) < 8:
            recommendations.append("Add more technical skills and certifications relevant to your field.")
            
        if len(experiences) < 4:
            recommendations.append("Include more quantifiable achievements with specific metrics (e.g., 'Increased sales by 25%').")
            
        # Check for action verbs in experiences
        weak_action_verbs = ["helped", "assisted", "worked on", "was responsible for"]
        strong_action_verbs = ["managed", "developed", "created", "implemented", "optimized", "led"]
        
        weak_count = sum(1 for exp in experiences 
                        for verb in weak_action_verbs if verb in exp.lower())
        strong_count = sum(1 for exp in experiences 
                          for verb in strong_action_verbs if verb in exp.lower())
                          
        if weak_count > strong_count:
            recommendations.append("Use stronger action verbs to describe your accomplishments (e.g., 'Led' instead of 'Helped').")
            
        # Check for metrics
        metrics_keywords = ["%", "increased", "decreased", "improved", "reduced", "grew", "$", "saved"]
        metrics_count = sum(1 for exp in experiences 
                           for keyword in metrics_keywords if keyword in exp.lower())
                           
        if metrics_count < len(experiences) / 2:
            recommendations.append("Include more quantifiable results to demonstrate impact (e.g., 'Reduced processing time by 40%').")
            
        # Job-specific recommendations
        if job_position and job_position in self.job_keywords:
            missing_keywords = []
            for keyword in self.job_keywords[job_position]:
                if keyword.lower() not in text.lower():
                    missing_keywords.append(keyword.title())
            
            if missing_keywords:
                recommendations.append(f"Consider adding these keywords relevant to {job_position.replace('-', ' ').title()}: {', '.join(missing_keywords[:5])}")
        
        # Formatting recommendations
        if "objective" not in text.lower() and "summary" not in text.lower():
            recommendations.append("Add a professional summary or objective at the beginning of your resume.")
            
        # Fallback recommendations if none were generated
        if not recommendations:
            recommendations.append("Review your resume for typos and grammatical errors.")
            recommendations.append("Ensure consistent formatting throughout the document.")
            recommendations.append("Tailor your resume for each job application.")
            
        return recommendations

    def analyze(self, text: str, job_position: Optional[str] = None) -> Dict:
        """
        Main analysis function that orchestrates the resume analysis.
        
        Args:
            text (str): Resume text to analyze
            job_position (Optional[str]): Target job position for keyword matching
            
        Returns:
            Dict: Analysis results including skills, experiences, score, feedback, and recommendations
        """
        # Extract skills and experiences
        skills = self.extract_skills(text)
        experiences = self.extract_experiences(text)
        
        # Calculate score
        score = self.calculate_score(text, skills, experiences)
        
        # Generate feedback and recommendations
        feedback = self.generate_feedback(text, skills, experiences, score)
        recommendations = self.generate_recommendations(text, skills, experiences, job_position)
        
        # Return structured results
        return {
            "skills": skills,
            "experiences": experiences,
            "score": score,
            "feedback": feedback,
            "recommendations": recommendations
        }