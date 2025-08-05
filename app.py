# AI Interview Simulator - Fixed Version
# app.py

import streamlit as st
import google.generativeai as genai
import os
import json
import time
import pandas as pd
from typing import Dict, List, Optional
from io import BytesIO
import base64
from dotenv import load_dotenv
from datetime import datetime, timedelta

# File processing imports
import PyPDF2
from docx import Document
import mammoth

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="AI Interview Simulator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling with timer
def load_custom_css():
    st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --primary-color: #4f46e5;
        --secondary-color: #7c3aed;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --danger-color: #ef4444;
        --background-color: #f8fafc;
        --surface-color: #ffffff;
        --text-color: #1f2937;
        --border-color: #e5e7eb;
    }
    
    /* Timer styling */
    .timer-container {
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1rem;
        font-size: 1.2rem;
        font-weight: bold;
    }
    
    .timer-warning {
        background: linear-gradient(90deg, var(--warning-color), #d97706);
        animation: pulse 1s infinite;
    }
    
    .timer-danger {
        background: linear-gradient(90deg, var(--danger-color), #dc2626);
        animation: pulse 0.5s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    /* Interview duration selection */
    .duration-card {
        padding: 1.5rem;
        border: 2px solid var(--border-color);
        border-radius: 10px;
        text-align: center;
        transition: all 0.3s ease;
        background: white;
        margin-bottom: 1rem;
    }
    
    .duration-card:hover {
        border-color: var(--primary-color);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2);
    }
    
    .duration-card.selected {
        border-color: var(--primary-color);
        background: linear-gradient(45deg, #f8fafc, #e0e7ff);
    }
    
    /* Question progress indicator */
    .question-progress {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Header styling */
    .header {
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    /* Progress bar styling */
    .progress-container {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .progress-bar {
        width: 100%;
        height: 8px;
        background-color: #e5e7eb;
        border-radius: 4px;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        transition: width 0.3s ease;
    }
    
    .stage-indicators {
        display: flex;
        justify-content: space-between;
        margin-top: 1rem;
    }
    
    .stage {
        display: flex;
        flex-direction: column;
        align-items: center;
        font-size: 0.875rem;
    }
    
    .stage-icon {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 0.5rem;
        font-weight: bold;
    }
    
    .stage-active {
        background-color: var(--primary-color);
        color: white;
    }
    
    .stage-completed {
        background-color: var(--success-color);
        color: white;
    }
    
    .stage-inactive {
        background-color: #e5e7eb;
        color: #6b7280;
    }
    
    /* Card styling */
    .card {
        background: white;
        border-radius: 10px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 1px solid var(--border-color);
    }
    
    /* Chat styling */
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding: 1rem;
        background: #f8fafc;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    .chat-message {
        margin-bottom: 1rem;
        padding: 1rem;
        border-radius: 10px;
        max-width: 80%;
    }
    
    .user-message {
        background: var(--primary-color);
        color: white;
        margin-left: auto;
    }
    
    .ai-message {
        background: white;
        color: var(--text-color);
        border: 1px solid var(--border-color);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
    }
    
    /* Success message */
    .success-message {
        background: linear-gradient(90deg, var(--success-color), #059669);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Error message */
    .error-message {
        background: linear-gradient(90deg, #ef4444, #dc2626);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Duration selection styling */
    .duration-button {
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        margin-bottom: 0.5rem;
    }
    
    .duration-button:hover {
        border-color: var(--primary-color);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2);
    }
    
    .duration-button.selected {
        border-color: var(--primary-color);
        background: linear-gradient(45deg, #f8fafc, #e0e7ff);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
    }
    
    /* HEARS feedback styling */
    .hears-section {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid var(--primary-color);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .hears-individual {
        background: #f8fafc;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 3px solid var(--secondary-color);
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        .header h1 {
            font-size: 2rem;
        }
        
        .chat-message {
            max-width: 95%;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# Gemini API Configuration
class GeminiClient:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            st.error("❌ Gemini API key not found! Please set GEMINI_API_KEY in your environment.")
            st.stop()
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
    
    def generate_questions(self, resume_text: str, job_details: Dict, num_questions: int) -> List[str]:
        """Generate behavioral interview questions based on resume and job details."""
        prompt = f"""
        You are an expert behavioral interviewer. Generate exactly {num_questions} behavioral interview questions based on the resume and job description provided.

        RESUME CONTENT:
        {resume_text}

        JOB DETAILS:
        - Title: {job_details.get('job_title', 'N/A')}
        - Company: {job_details.get('company_name', 'N/A')}
        - Description: {job_details.get('job_description', 'N/A')}
        - Experience Level: {job_details.get('experience_years', 0)} years
        - Interview Duration: {job_details.get('duration', 15)} minutes

        REQUIREMENTS:
        1. Generate exactly {num_questions} questions - no more, no less
        2. Focus on HEARS method (Headline, Events, Actions, Results, Significance)
        3. Tailor questions to candidate's background and job requirements
        4. Include variety: leadership, problem-solving, conflict resolution, teamwork, adaptability, communication
        5. Match difficulty to experience level and interview duration
        6. Make questions specific and actionable
        7. Ensure questions encourage detailed responses covering all HEARS elements

        IMPORTANT: Return your response in this EXACT format as a valid JSON array:
        ["Question 1 text here", "Question 2 text here", "Question 3 text here"]

        Do not include any other text, explanations, or formatting. Just the JSON array with exactly {num_questions} questions.
        """
        
        try:
            response = self.model.generate_content(prompt)
            questions_text = response.text.strip()
            
            # Debug print
            print(f"API Response: {questions_text}")
            
            # Clean up the response text
            questions_text = questions_text.strip()
            
            # Remove any markdown formatting if present
            if questions_text.startswith('```'):
                lines = questions_text.split('\n')
                questions_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else questions_text
            
            # Try to extract JSON array
            start_idx = questions_text.find('[')
            end_idx = questions_text.rfind(']') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_text = questions_text[start_idx:end_idx]
                try:
                    questions = json.loads(json_text)
                    if isinstance(questions, list) and len(questions) >= num_questions:
                        return questions[:num_questions]
                    elif isinstance(questions, list):
                        # If we got fewer questions than expected, pad with fallback
                        fallback = self._get_fallback_questions(num_questions - len(questions))
                        return questions + fallback
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    pass
            
            # Enhanced fallback parsing
            questions = []
            lines = questions_text.split('\n')
            
            for line in lines:
                line = line.strip()
                # Try different patterns
                if line.startswith('"') and line.endswith('",'):
                    questions.append(line[1:-2])
                elif line.startswith('"') and line.endswith('"'):
                    questions.append(line[1:-1])
                elif line.startswith('- '):
                    questions.append(line[2:])
                elif line.startswith(f'{len(questions)+1}.'):
                    questions.append(line[len(f'{len(questions)+1}.'):].strip())
            
            # If we still don't have enough questions, use fallbacks
            if len(questions) < num_questions:
                fallback_questions = self._get_fallback_questions(num_questions - len(questions))
                questions.extend(fallback_questions)
            
            return questions[:num_questions]
                
        except Exception as e:
            st.error(f"Error generating questions: {str(e)}")
            return self._get_fallback_questions(num_questions)
    
    def get_interview_response(self, current_question: str, user_response: str, conversation_history: List) -> str:
        """Generate interviewer response based on user's answer."""
        history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history[-4:]])
        
        prompt = f"""
        You are conducting a behavioral interview using the HEARS methodology. Current context:

        QUESTION ASKED: {current_question}
        CANDIDATE'S RESPONSE: {user_response}
        CONVERSATION HISTORY: {history_text}

        Based on their response, check if they covered the HEARS elements:
        - H (Headline): Brief summary of the situation
        - E (Events): Specific situation/challenge described
        - A (Actions): Detailed actions they took
        - R (Results): Outcomes and measurable impact
        - S (Significance): Skills demonstrated and learning

        Respond based on what's missing:
        1. If missing Headlines/Events, ask for situation context
        2. If missing Actions, ask for specific steps they took
        3. If missing Results, ask "What was the outcome and impact?"
        4. If missing Significance, ask about skills used or lessons learned
        5. If response covers all HEARS elements well, acknowledge positively and indicate readiness for next question

        Keep responses encouraging, professional, and focused on one follow-up at a time.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Thank you for sharing that. Could you tell me more about the specific actions you took and the results you achieved?"
    
    def generate_individual_feedback(self, question: str, answer: str, job_details: Dict) -> str:
        """Generate HEARS feedback for individual question."""
        prompt = f"""
        Analyze this single interview question and answer using the HEARS methodology:

        QUESTION: {question}
        CANDIDATE'S ANSWER: {answer}
        JOB CONTEXT: {job_details.get('job_title', 'N/A')} at {job_details.get('company_name', 'N/A')}

        Provide feedback in this format:

        ## 🎯 Question Analysis

        **H (Headline):** [Did they provide a clear situation summary? Rate 1-10]
        **E (Events):** [Did they describe specific events/challenges? Rate 1-10]
        **A (Actions):** [Did they detail their specific actions? Rate 1-10]
        **R (Results):** [Did they share measurable outcomes? Rate 1-10]
        **S (Significance):** [Did they demonstrate skills/learning? Rate 1-10]

        **Overall Score:** X/10
        **Strengths:** [2-3 key strengths in this response]
        **Areas for Improvement:** [1-2 specific suggestions]
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Unable to generate detailed feedback for this question."
    
    def generate_overall_feedback(self, all_responses: List, job_details: Dict) -> str:
        """Generate comprehensive HEARS methodology feedback."""
        responses_text = "\n\n".join([
            f"Q{i+1}: {response['question']}\nA{i+1}: {response['answer']}"
            for i, response in enumerate(all_responses)
        ])
        
        prompt = f"""
        Analyze this complete behavioral interview using the HEARS methodology:

        INTERVIEW RESPONSES: {responses_text}
        JOB CONTEXT: {job_details}
        INTERVIEW DURATION: {job_details.get('duration', 15)} minutes
        TOTAL QUESTIONS: {len(all_responses)}

        Provide comprehensive feedback in this EXACT format:

        # 🎯 OVERALL INTERVIEW FEEDBACK REPORT

        ## **📰 HEADLINE ANALYSIS**
        [How well did candidate provide situation summaries across all questions]
        **Headline Score: X/10**

        ## **📅 EVENTS ANALYSIS**  
        [Quality of situations/challenges described across all responses]
        **Events Score: X/10**
        • Key Event 1: [Brief description]
        • Key Event 2: [Brief description] 
        • Key Event 3: [Brief description]

        ## **⚡ ACTIONS ANALYSIS**
        [Depth and specificity of actions described]
        **Actions Score: X/10**
        • Strong Action Example: [Description]
        • Area for Improvement: [Suggestion]

        ## **🎊 RESULTS ANALYSIS**
        [Quality of outcomes and measurable impacts shared]
        **Results Score: X/10**
        • Quantified Result 1: [Description with numbers]
        • Quantified Result 2: [Description with numbers]

        ## **💡 SIGNIFICANCE ANALYSIS**
        **Skills Demonstrated:**
        - Leadership: [Analysis] - **Score: X/10**
        - Problem-Solving: [Analysis] - **Score: X/10**  
        - Communication: [Analysis] - **Score: X/10**
        - Teamwork: [Analysis] - **Score: X/10**
        - Adaptability: [Analysis] - **Score: X/10**

        ## **📈 OVERALL ASSESSMENT**
        **Interview Duration Performance:** [How well they used the time]
        **HEARS Methodology Adherence:** X/10
        **Top 3 Strengths:** [List with specific examples]
        **Top 3 Development Areas:** [Specific, actionable improvements]
        **Overall Interview Score:** **X/10**
        **Hiring Recommendation:** **[STRONG HIRE/HIRE/MAYBE/PASS]**

        ## **🚀 IMPROVEMENT RECOMMENDATIONS**
        **For Future Interviews:**
        [Specific, actionable advice based on HEARS gaps]
        
        **For Professional Development:**
        [Skills to develop based on responses]
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error generating comprehensive feedback: {str(e)}"
    
    def _get_fallback_questions(self, num_questions: int) -> List[str]:
        """Fallback questions if API fails."""
        fallback_questions = [
            "Tell me about a time when you had to lead a team through a difficult project. What was your approach and what were the results?",
            "Describe a situation where you had to solve a complex problem with limited resources. How did you handle it and what did you learn?",
            "Can you share an example of when you had to work with a difficult team member or stakeholder? What actions did you take?",
            "Tell me about a time when you had to adapt quickly to a significant change in your work environment. What was the outcome?",
            "Describe a situation where you made a mistake. How did you handle it and what did you learn from the experience?",
            "Give me an example of when you had to influence others without having direct authority over them. What was the result?",
            "Tell me about a time when you had to work under tight deadlines. How did you prioritize and manage your time?",
            "Describe a situation where you had to learn a new skill quickly to complete a project. What was the impact?",
            "Can you share an example of when you had to give difficult feedback to a colleague? How did you approach it?",
            "Tell me about a time when you had to make a decision with incomplete information. What was the outcome?",
            "Describe a situation where you had to manage competing priorities from different stakeholders. How did you handle it?",
            "Give me an example of when you went above and beyond what was expected in your role. What were the results?"
        ]
        
        return fallback_questions[:num_questions]

# File Processing Functions
class FileProcessor:
    @staticmethod
    def validate_file(uploaded_file) -> tuple[bool, str]:
        """Validate uploaded file size and format."""
        if uploaded_file is None:
            return False, "No file uploaded"
        
        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB in bytes
        if uploaded_file.size > max_size:
            return False, f"File size ({uploaded_file.size / 1024 / 1024:.1f}MB) exceeds maximum allowed size (10MB)"
        
        # Check file format
        allowed_extensions = ['.pdf', '.doc', '.docx', '.txt']
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        if file_extension not in allowed_extensions:
            return False, f"Unsupported file format. Please upload: {', '.join(allowed_extensions)}"
        
        return True, "File validated successfully"
    
    @staticmethod
    def extract_text_from_pdf(pdf_file) -> str:
        """Extract text from PDF file."""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    @staticmethod
    def extract_text_from_docx(docx_file) -> str:
        """Extract text from DOCX file."""
        try:
            doc = Document(docx_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading DOCX: {str(e)}")
    
    @staticmethod
    def extract_text_from_doc(doc_file) -> str:
        """Extract text from DOC file using mammoth."""
        try:
            result = mammoth.extract_raw_text(doc_file)
            return result.value.strip()
        except Exception as e:
            raise Exception(f"Error reading DOC: {str(e)}")
    
    @staticmethod
    def extract_text_from_txt(txt_file) -> str:
        """Extract text from TXT file."""
        try:
            return txt_file.read().decode('utf-8').strip()
        except Exception as e:
            raise Exception(f"Error reading TXT: {str(e)}")
    
    @classmethod
    def process_resume_file(cls, uploaded_file) -> tuple[bool, str]:
        """Process uploaded resume file and extract text."""
        is_valid, message = cls.validate_file(uploaded_file)
        if not is_valid:
            return False, message
        
        try:
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
            
            if file_extension == '.pdf':
                text = cls.extract_text_from_pdf(uploaded_file)
            elif file_extension == '.docx':
                text = cls.extract_text_from_docx(uploaded_file)
            elif file_extension == '.doc':
                text = cls.extract_text_from_doc(uploaded_file)
            elif file_extension == '.txt':
                text = cls.extract_text_from_txt(uploaded_file)
            else:
                return False, "Unsupported file format"
            
            if len(text.strip()) < 50:
                return False, "Resume appears to be empty or too short. Please upload a valid resume."
            
            return True, text
        
        except Exception as e:
            return False, f"Error processing file: {str(e)}"

# Timer functionality
class InterviewTimer:
    def __init__(self, duration_minutes: int):
        self.duration_seconds = duration_minutes * 60
        self.start_time = None
        self.question_start_time = None
    
    def start_interview(self):
        self.start_time = datetime.now()
    
    def start_question(self):
        self.question_start_time = datetime.now()
    
    def get_remaining_time(self) -> int:
        if not self.start_time:
            return self.duration_seconds
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        remaining = max(0, self.duration_seconds - elapsed)
        return int(remaining)
    
    def get_question_time(self) -> int:
        if not self.question_start_time:
            return 0
        
        elapsed = (datetime.now() - self.question_start_time).total_seconds()
        return int(elapsed)
    
    def format_time(self, seconds: int) -> str:
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

# Session State Management
def initialize_session_state():
    """Initialize all session state variables."""
    defaults = {
        'stage': 'upload',  # upload, details, interview, feedback
        'resume_text': "",
        'job_details': {},
        'interview_duration': 15,  # Default to 15 minutes
        'num_questions': 3,  # Default to 3 questions
        'questions': [],
        'current_question_idx': 0,
        'conversation': [],
        'question_responses': [],  # Store individual Q&A pairs
        'individual_feedback': [],  # Store individual question feedback
        'overall_feedback': "",
        'interview_completed': False,
        'timer': None,
        'question_timer_start': None,
        'gemini_client': None,
        'duration_selected': False  # Track if user has selected a duration
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    # Initialize Gemini client if not exists
    if st.session_state.gemini_client is None:
        try:
            st.session_state.gemini_client = GeminiClient()
        except Exception as e:
            st.error(f"Failed to initialize AI client: {str(e)}")

# UI Components
def render_header():
    """Render application header."""
    st.markdown("""
    <div class="header">
        <h1>🚀 AI Interview Simulator</h1>
        <p>Practice behavioral interviews with AI-powered HEARS methodology feedback</p>
    </div>
    """, unsafe_allow_html=True)

def render_progress_bar():
    """Render progress bar with stage indicators."""
    stages = ['upload', 'details', 'interview', 'feedback']
    stage_names = ['📄 Upload Resume', '📝 Job Details', '💬 Interview', '📊 Feedback']
    current_stage_idx = stages.index(st.session_state.stage)
    progress_percentage = (current_stage_idx / (len(stages) - 1)) * 100
    
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-bar">
            <div class="progress-fill" style="width: {progress_percentage}%"></div>
        </div>
        <div class="stage-indicators">
    """, unsafe_allow_html=True)
    
    for i, (stage, name) in enumerate(zip(stages, stage_names)):
        if i < current_stage_idx:
            icon_class = "stage-completed"
            icon = "✓"
        elif i == current_stage_idx:
            icon_class = "stage-active"
            icon = str(i + 1)
        else:
            icon_class = "stage-inactive"
            icon = str(i + 1)
        
        st.markdown(f"""
            <div class="stage">
                <div class="stage-icon {icon_class}">{icon}</div>
                <span>{name}</span>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)

def render_interview_timer():
    """Render interview timer."""
    if st.session_state.timer and st.session_state.stage == 'interview':
        remaining = st.session_state.timer.get_remaining_time()
        total_duration = st.session_state.interview_duration * 60
        
        # Determine timer color based on remaining time
        timer_class = "timer-container"
        if remaining < total_duration * 0.25:  # Less than 25% time left
            timer_class += " timer-danger"
        elif remaining < total_duration * 0.5:  # Less than 50% time left
            timer_class += " timer-warning"
        
        time_str = st.session_state.timer.format_time(remaining)
        
        st.markdown(f"""
        <div class="{timer_class}">
            ⏱️ Time Remaining: {time_str}
        </div>
        """, unsafe_allow_html=True)
        
        # Auto-refresh timer display
        if remaining <= 0:
            st.session_state.interview_completed = True
            st.session_state.stage = 'feedback'
            st.rerun()

def render_sidebar():
    """Render sidebar with progress and controls."""
    with st.sidebar:
        st.title("📋 Interview Progress")
        
        # Interview duration info
        if st.session_state.interview_duration:
            st.info(f"📅 Interview Duration: {st.session_state.interview_duration} minutes")
            st.info(f"📝 Total Questions: {st.session_state.num_questions}")
        
        # Current stage info
        stage_info = {
            'upload': "Upload your resume to get started",
            'details': "Select duration and provide job details",
            'interview': f"Question {min(st.session_state.current_question_idx + 1, len(st.session_state.questions))} of {len(st.session_state.questions)}" if st.session_state.questions else "Preparing interview questions...",
            'feedback': "Review your HEARS methodology feedback"
        }
        
        st.success(stage_info.get(st.session_state.stage, "Unknown stage"))
        
        # Resume info if uploaded
        if st.session_state.resume_text:
            st.success("✅ Resume uploaded successfully")
            st.write(f"**Resume length:** {len(st.session_state.resume_text)} characters")
        
        # Job details if provided
        if st.session_state.job_details:
            st.success("✅ Job details provided")
            if 'job_title' in st.session_state.job_details:
                st.write(f"**Position:** {st.session_state.job_details['job_title']}")
        
        # Interview progress if in progress
        if st.session_state.stage == 'interview' and st.session_state.questions:
            progress = min(st.session_state.current_question_idx / max(len(st.session_state.questions), 1), 1.0)
            progress = max(progress, 0.0)
            st.progress(progress)
            
            current_q = min(st.session_state.current_question_idx, len(st.session_state.questions))
            st.write(f"Questions completed: {current_q}/{len(st.session_state.questions)}")
            
            # Show time per question average
            if st.session_state.timer:
                elapsed = st.session_state.interview_duration * 60 - st.session_state.timer.get_remaining_time()
                if current_q > 0:
                    avg_time = elapsed / current_q
                    st.write(f"Average time per question: {int(avg_time//60)}:{int(avg_time%60):02d}")
        
        st.divider()
        
        # Help section
        st.subheader("💡 HEARS Method Tips")
        if st.session_state.stage == 'upload':
            st.write("• Ensure your resume is up-to-date\n• Include relevant experience and skills\n• Supported formats: PDF, DOC, DOCX, TXT")
        elif st.session_state.stage == 'details':
            st.write("• Choose appropriate interview duration\n• Provide detailed job description\n• Include specific requirements")
        elif st.session_state.stage == 'interview':
            st.write("**HEARS Method:**\n• **H**eadline: Brief situation summary\n• **E**vents: Specific challenges\n• **A**ctions: Your detailed actions\n• **R**esults: Measurable outcomes\n• **S**ignificance: Skills & learning")
        elif st.session_state.stage == 'feedback':
            st.write("• Review individual question feedback\n• Focus on HEARS methodology gaps\n• Practice recommended improvements")
        
        st.divider()
        
        # Restart option
        if st.button("🔄 Start New Interview", type="secondary"):
            for key in ['stage', 'resume_text', 'job_details', 'questions', 'current_question_idx', 'conversation', 'question_responses', 'individual_feedback', 'overall_feedback', 'interview_completed', 'timer', 'question_timer_start', 'duration_selected']:
                if key in st.session_state:
                    del st.session_state[key]
            # Reset defaults
            st.session_state.interview_duration = 15
            st.session_state.num_questions = 3
            st.rerun()

# Stage Functions
def render_upload_stage():
    """Render resume upload stage."""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("📄 Upload Your Resume")
    st.write("Start by uploading your resume. We support PDF, DOC, DOCX, and TXT formats.")
    
    uploaded_file = st.file_uploader(
        "Choose your resume file",
        type=['pdf', 'doc', 'docx', 'txt'],
        help="Maximum file size: 10MB"
    )
    
    if uploaded_file is not None:
        with st.spinner("Processing your resume..."):
            success, result = FileProcessor.process_resume_file(uploaded_file)
            
            if success:
                st.session_state.resume_text = result
                st.markdown('<div class="success-message">✅ Resume uploaded and processed successfully!</div>', unsafe_allow_html=True)
                
                # Show preview
                with st.expander("📖 Resume Preview"):
                    preview_text = result[:500] + "..." if len(result) > 500 else result
                    st.text(preview_text)
                
                if st.button("Continue to Job Details", type="primary"):
                    st.session_state.stage = 'details'
                    st.rerun()
            else:
                st.markdown(f'<div class="error-message">❌ {result}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_details_stage():
    """Render job details collection stage with duration selection."""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("📝 Interview Setup")
    st.write("Select your interview duration and provide job details for personalized questions.")
    
    # Interview Duration Selection
    st.subheader("⏱️ Interview Duration")
    st.write("Choose how long you'd like your practice interview to be:")
    
    # Duration selection with radio buttons for better state management
    duration_options = {
        "15 Minutes (3 Questions) - Quick practice": (15, 3),
        "30 Minutes (6 Questions) - Standard length": (30, 6),
        "45 Minutes (9 Questions) - Comprehensive": (45, 9),
        "60 Minutes (12 Questions) - Extended practice": (60, 12)
    }
    
    # Determine current selection for radio button
    current_selection = None
    for option, (duration, questions) in duration_options.items():
        if st.session_state.interview_duration == duration and st.session_state.num_questions == questions:
            current_selection = option
            break
    
    # If no current selection found, default to first option
    if current_selection is None:
        current_selection = list(duration_options.keys())[0]
        st.session_state.interview_duration = 15
        st.session_state.num_questions = 3
    
    selected_option = st.radio(
        "Select interview duration:",
        options=list(duration_options.keys()),
        index=list(duration_options.keys()).index(current_selection),
        key="duration_radio"
    )
    
    # Update session state based on selection
    duration, num_questions = duration_options[selected_option]
    st.session_state.interview_duration = duration
    st.session_state.num_questions = num_questions
    st.session_state.duration_selected = True
    
    st.success(f"✅ Selected: {duration} minutes ({num_questions} questions)")
    
    st.divider()
    
    # Job Details Form
    st.subheader("💼 Job Details")
    st.write("Provide information about the position you're interviewing for:")
    
    with st.form("job_details_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            job_title = st.text_input("Job Title *", placeholder="e.g., Senior Software Engineer")
            company_name = st.text_input("Company Name *", placeholder="e.g., Tech Corp Inc.")
            experience_years = st.number_input("Years of Experience Required", min_value=0, max_value=50, value=3)
        
        with col2:
            industry = st.selectbox(
                "Industry (Optional)",
                ["", "Technology", "Healthcare", "Finance", "Marketing", "Sales", "Education", "Manufacturing", "Retail", "Other"]
            )
        
        job_description = st.text_area(
            "Job Description *",
            placeholder="Paste the job description here, including responsibilities, requirements, and qualifications...",
            height=200
        )
        
        submitted = st.form_submit_button("Generate Interview Questions", type="primary")
        
        if submitted:
            if not job_title or not company_name or not job_description:
                st.error("Please fill in all required fields (marked with *)")
            else:
                job_details = {
                    'job_title': job_title,
                    'company_name': company_name,
                    'job_description': job_description,
                    'experience_years': experience_years,
                    'industry': industry,
                    'duration': st.session_state.interview_duration
                }
                
                st.session_state.job_details = job_details
                
                # Generate questions based on selected duration
                with st.spinner(f"Generating {st.session_state.num_questions} personalized interview questions..."):
                    try:
                        questions = st.session_state.gemini_client.generate_questions(
                            st.session_state.resume_text,
                            job_details,
                            st.session_state.num_questions
                        )
                        
                        # Debugging: Show what questions were generated
                        st.write(f"DEBUG: Generated {len(questions)} questions:")
                        for i, q in enumerate(questions):
                            st.write(f"{i+1}. {q}")
                        
                        st.session_state.questions = questions
                        
                        # Initialize timer
                        st.session_state.timer = InterviewTimer(st.session_state.interview_duration)
                        
                        st.session_state.stage = 'interview'
                        st.success(f"Questions generated successfully! Starting your {st.session_state.interview_duration}-minute interview with {len(questions)} questions...")
                        time.sleep(3)  # Give user time to see the debug info
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error generating questions: {str(e)}")
                        st.error("Please try again or contact support if the issue persists.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_interview_stage():
    """Render interactive interview stage with timer."""
    if not st.session_state.questions:
        st.error("No questions available. Please go back and regenerate questions.")
        return
    
    # Start interview timer if not started
    if st.session_state.timer and not st.session_state.timer.start_time:
        st.session_state.timer.start_interview()
    
    # Render timer
    render_interview_timer()
    
    st.title("💬 Behavioral Interview (HEARS Method)")
    
    # Question progress indicator
    progress_percent = (st.session_state.current_question_idx / len(st.session_state.questions)) * 100
    st.markdown(f"""
    <div class="question-progress">
        <span><strong>Question {st.session_state.current_question_idx + 1} of {len(st.session_state.questions)}</strong></span>
        <span><strong>Progress: {progress_percent:.0f}%</strong></span>
    </div>
    """, unsafe_allow_html=True)
    
    # Interview progress bar
    progress = min(st.session_state.current_question_idx / len(st.session_state.questions), 1.0)
    st.progress(progress)
    
    # Current question or completion
    if st.session_state.current_question_idx < len(st.session_state.questions):
        current_question = st.session_state.questions[st.session_state.current_question_idx]
        
        # Start question timer if not started
        if not st.session_state.question_timer_start:
            st.session_state.question_timer_start = datetime.now()
            if st.session_state.timer:
                st.session_state.timer.start_question()
        
        # Display current question
        st.markdown(f"""
        <div class="card">
            <h4>Current Question:</h4>
            <p style="font-size: 1.1em; font-weight: 500; color: var(--primary-color);">{current_question}</p>
            <div style="background: #f0f9ff; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                <strong>💡 HEARS Method Reminder:</strong><br>
                <strong>H</strong>eadline: Brief situation summary<br>
                <strong>E</strong>vents: Specific challenges/context<br>
                <strong>A</strong>ctions: Your detailed actions<br>
                <strong>R</strong>esults: Measurable outcomes<br>
                <strong>S</strong>ignificance: Skills used & lessons learned
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # User response input
        with st.form(f"response_form_{st.session_state.current_question_idx}"):
            user_response = st.text_area(
                "Your Answer (use HEARS method):",
                placeholder="Provide a comprehensive answer covering Headline, Events, Actions, Results, and Significance...",
                height=200,
                key=f"response_{st.session_state.current_question_idx}"
            )
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                submitted = st.form_submit_button("Submit Answer", type="primary")
            
            with col2:
                if st.form_submit_button("Skip Question", type="secondary"):
                    # Record skipped question
                    st.session_state.question_responses.append({
                        'question': current_question,
                        'answer': '[Question Skipped]',
                        'question_number': st.session_state.current_question_idx + 1
                    })
                    
                    st.session_state.current_question_idx += 1
                    st.session_state.question_timer_start = None
                    st.rerun()
            
            if submitted and user_response.strip():
                # Record the Q&A pair
                st.session_state.question_responses.append({
                    'question': current_question,
                    'answer': user_response.strip(),
                    'question_number': st.session_state.current_question_idx + 1
                })
                
                # Generate individual feedback for this question
                with st.spinner("Analyzing your response using HEARS methodology..."):
                    try:
                        individual_feedback = st.session_state.gemini_client.generate_individual_feedback(
                            current_question,
                            user_response.strip(),
                            st.session_state.job_details
                        )
                        st.session_state.individual_feedback.append({
                            'question_number': st.session_state.current_question_idx + 1,
                            'feedback': individual_feedback
                        })
                    except Exception as e:
                        st.session_state.individual_feedback.append({
                            'question_number': st.session_state.current_question_idx + 1,
                            'feedback': f"Unable to generate feedback: {str(e)}"
                        })
                
                # Move to next question
                st.session_state.current_question_idx += 1
                st.session_state.question_timer_start = None
                
                if st.session_state.current_question_idx >= len(st.session_state.questions):
                    st.session_state.interview_completed = True
                
                st.rerun()
    
    else:
        # Interview completed
        st.session_state.interview_completed = True
        st.markdown("""
        <div class="success-message">
            <h3>🎉 Interview Completed!</h3>
            <p>Excellent work! You've completed all questions. Click below to get your comprehensive HEARS methodology feedback.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📊 Get My HEARS Feedback Report", type="primary"):
            with st.spinner("Generating your comprehensive HEARS methodology feedback report..."):
                try:
                    # Generate overall feedback
                    overall_feedback = st.session_state.gemini_client.generate_overall_feedback(
                        st.session_state.question_responses,
                        st.session_state.job_details
                    )
                    st.session_state.overall_feedback = overall_feedback
                    st.session_state.stage = 'feedback'
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating feedback: {str(e)}")

def render_feedback_stage():
    """Render comprehensive HEARS feedback report."""
    st.title("📊 HEARS Methodology Feedback Report")
    
    if not st.session_state.question_responses:
        st.error("No interview responses available. Please complete the interview first.")
        return
    
    # Interview Summary
    st.markdown(f"""
    <div class="hears-section">
        <h3>📋 Interview Summary</h3>
        <p><strong>Position:</strong> {st.session_state.job_details.get('job_title', 'N/A')}</p>
        <p><strong>Company:</strong> {st.session_state.job_details.get('company_name', 'N/A')}</p>
        <p><strong>Duration:</strong> {st.session_state.interview_duration} minutes</p>
        <p><strong>Questions Completed:</strong> {len(st.session_state.question_responses)} of {st.session_state.num_questions}</p>
        <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Individual Question Feedback
    st.subheader("📝 Individual Question Analysis")
    
    for i, response in enumerate(st.session_state.question_responses):
        with st.expander(f"Question {response['question_number']}: Analysis", expanded=False):
            st.markdown(f"""
            <div class="hears-individual">
                <h4>Question:</h4>
                <p>{response['question']}</p>
                
                <h4>Your Answer:</h4>
                <p style="background: #f8fafc; padding: 1rem; border-radius: 5px;">{response['answer']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Display individual feedback if available
            if i < len(st.session_state.individual_feedback):
                st.markdown(st.session_state.individual_feedback[i]['feedback'])
            else:
                st.info("Individual feedback not available for this question.")
    
    st.divider()
    
    # Overall HEARS Feedback
    st.subheader("🎯 Overall HEARS Analysis")
    
    if st.session_state.overall_feedback:
        st.markdown('<div class="hears-section">', unsafe_allow_html=True)
        st.markdown(st.session_state.overall_feedback)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Generating overall feedback...")
        if st.button("Generate Overall Feedback"):
            with st.spinner("Creating comprehensive HEARS analysis..."):
                try:
                    overall_feedback = st.session_state.gemini_client.generate_overall_feedback(
                        st.session_state.question_responses,
                        st.session_state.job_details
                    )
                    st.session_state.overall_feedback = overall_feedback
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating overall feedback: {str(e)}")
    
    # Action buttons
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📄 Download Report", type="secondary"):
            # Create comprehensive downloadable report
            report_content = f"""
# AI Interview Simulator - HEARS Methodology Report

**Interview Details:**
- Position: {st.session_state.job_details.get('job_title', 'N/A')}
- Company: {st.session_state.job_details.get('company_name', 'N/A')}
- Duration: {st.session_state.interview_duration} minutes
- Questions Completed: {len(st.session_state.question_responses)}/{st.session_state.num_questions}
- Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## Individual Question Analysis

"""
            
            # Add individual Q&A and feedback
            for i, response in enumerate(st.session_state.question_responses):
                report_content += f"""
### Question {response['question_number']}

**Question:** {response['question']}

**Your Answer:** {response['answer']}

**HEARS Analysis:**
"""
                if i < len(st.session_state.individual_feedback):
                    report_content += f"{st.session_state.individual_feedback[i]['feedback']}\n\n"
                else:
                    report_content += "Individual feedback not available.\n\n"
            
            # Add overall feedback
            report_content += f"""
---

## Overall HEARS Analysis

{st.session_state.overall_feedback if st.session_state.overall_feedback else 'Overall feedback not generated.'}

---

*Generated by AI Interview Simulator using HEARS Methodology*
"""
            
            st.download_button(
                label="Download Complete HEARS Report",
                data=report_content,
                file_name=f"interview_hears_report_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown"
            )
    
    with col2:
        if st.button("🔄 Practice Again", type="primary"):
            # Reset for new interview with same job details
            for key in ['stage', 'questions', 'current_question_idx', 'conversation', 'question_responses', 'individual_feedback', 'overall_feedback', 'interview_completed', 'timer', 'question_timer_start']:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.stage = 'details'
            st.rerun()
    
    with col3:
        if st.button("📝 New Position", type="secondary"):
            # Reset everything for completely new interview
            for key in ['stage', 'job_details', 'interview_duration', 'num_questions', 'questions', 'current_question_idx', 'conversation', 'question_responses', 'individual_feedback', 'overall_feedback', 'interview_completed', 'timer', 'question_timer_start', 'duration_selected']:
                if key in st.session_state:
                    del st.session_state[key]
            # Reset to defaults
            st.session_state.interview_duration = 15
            st.session_state.num_questions = 3
            st.session_state.stage = 'details'
            st.rerun()
    
    with col4:
        if st.button("🏠 Start Over", type="secondary"):
            # Complete reset
            for key in list(st.session_state.keys()):
                if key != 'gemini_client':
                    del st.session_state[key]
            # Reset to defaults
            st.session_state.interview_duration = 15
            st.session_state.num_questions = 3
            st.rerun()

# Main Application
def main():
    """Main application entry point."""
    load_custom_css()
    initialize_session_state()
    
    render_header()
    render_progress_bar()
    render_sidebar()
    
    # Route to appropriate stage
    if st.session_state.stage == 'upload':
        render_upload_stage()
    elif st.session_state.stage == 'details':
        render_details_stage()
    elif st.session_state.stage == 'interview':
        render_interview_stage()
    elif st.session_state.stage == 'feedback':
        render_feedback_stage()
    else:
        st.error("Unknown stage. Please restart the application.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6b7280; font-size: 0.875rem;">
        Made with ❤️ using Streamlit and Google Gemini AI<br>
        Enhanced with HEARS Methodology for comprehensive interview feedback 🚀
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
