# AI Interview Simulator - Complete Streamlit Application
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

# Custom CSS for professional styling
def load_custom_css():
    st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --primary-color: #4f46e5;
        --secondary-color: #7c3aed;
        --success-color: #10b981;
        --background-color: #f8fafc;
        --surface-color: #ffffff;
        --text-color: #1f2937;
        --border-color: #e5e7eb;
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
    
    /* File upload area */
    .upload-area {
        border: 2px dashed var(--primary-color);
        border-radius: 10px;
        padding: 3rem;
        text-align: center;
        background: linear-gradient(45deg, #f8fafc, #f1f5f9);
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        border-color: var(--secondary-color);
        background: linear-gradient(45deg, #f1f5f9, #e2e8f0);
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
    
    /* Loading animation */
    .loading {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem;
    }
    
    .spinner {
        border: 3px solid #f3f3f3;
        border-top: 3px solid var(--primary-color);
        border-radius: 50%;
        width: 30px;
        height: 30px;
        animation: spin 1s linear infinite;
        margin-right: 1rem;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Feedback report styling */
    .feedback-report {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    }
    
    .feedback-section {
        margin-bottom: 2rem;
        padding: 1.5rem;
        border-left: 4px solid var(--primary-color);
        background: #f8fafc;
        border-radius: 0 8px 8px 0;
    }
    
    .competency-score {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 0;
        border-bottom: 1px solid #e5e7eb;
    }
    
    .score-badge {
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.875rem;
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
        
        .stage-indicators {
            flex-wrap: wrap;
            gap: 1rem;
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
    
    def generate_questions(self, resume_text: str, job_details: Dict) -> List[str]:
        """Generate behavioral interview questions based on resume and job details."""
        prompt = f"""
        Based on the following resume and job description, generate exactly 6 behavioral interview questions.

        RESUME CONTENT:
        {resume_text}

        JOB DETAILS:
        - Title: {job_details.get('job_title', 'N/A')}
        - Company: {job_details.get('company_name', 'N/A')}
        - Description: {job_details.get('job_description', 'N/A')}
        - Experience Level: {job_details.get('experience_years', 0)} years

        REQUIREMENTS:
        1. Focus on STAR method (Situation, Task, Action, Result)
        2. Tailor questions to candidate's background and job requirements
        3. Include variety: leadership, problem-solving, conflict resolution, teamwork, adaptability
        4. Match difficulty to experience level
        5. Make questions specific and actionable

        Return ONLY a JSON array of questions:
        ["Question 1 text here", "Question 2 text here", "Question 3 text here", "Question 4 text here", "Question 5 text here", "Question 6 text here"]
        """
        
        try:
            response = self.model.generate_content(prompt)
            questions_text = response.text.strip()
            
            # Extract JSON from response
            if questions_text.startswith('[') and questions_text.endswith(']'):
                questions = json.loads(questions_text)
                return questions
            else:
                # Fallback parsing
                lines = questions_text.split('\n')
                questions = []
                for line in lines:
                    if line.strip().startswith('"') and line.strip().endswith('"'):
                        questions.append(line.strip()[1:-1])
                return questions[:6]
                
        except Exception as e:
            st.error(f"Error generating questions: {str(e)}")
            return self._get_fallback_questions()
    
    def get_interview_response(self, current_question: str, user_response: str, conversation_history: List) -> str:
        """Generate interviewer response based on user's answer."""
        history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history[-4:]])
        
        prompt = f"""
        You are conducting a behavioral interview. Current context:

        QUESTION ASKED: {current_question}
        CANDIDATE'S RESPONSE: {user_response}
        CONVERSATION HISTORY: {history_text}

        Based on their response:
        1. If the answer lacks detail, ask for specifics about their actions or the situation
        2. If missing results/outcomes, ask "What was the final result?"
        3. If the response is complete with STAR details, acknowledge it positively and indicate readiness for the next question
        4. Keep responses encouraging and professional
        5. Ask only ONE follow-up question at a time

        Respond naturally as a friendly interviewer would.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Thank you for sharing that. Could you tell me more about the specific actions you took in that situation?"
    
    def generate_feedback(self, conversation: List, job_details: Dict) -> str:
        """Generate HEARS methodology feedback."""
        responses_text = "\n\n".join([
            f"Q: {msg['content']}\nA: {conversation[i+1]['content'] if i+1 < len(conversation) else 'No response'}"
            for i, msg in enumerate(conversation) if msg['role'] == 'assistant' and 'question' in msg.get('type', '')
        ])
        
        prompt = f"""
        Analyze this complete behavioral interview using the HEARS methodology:

        CANDIDATE RESPONSES: {responses_text}
        JOB CONTEXT: {job_details}

        Provide comprehensive feedback in this EXACT format:

        # 🎯 INTERVIEW FEEDBACK REPORT

        ## **HEADLINE**
        [2-3 sentence overall performance summary]

        ## **📅 EVENTS**  
        [Key situations/challenges the candidate described]
        • Event 1: [Brief description]
        • Event 2: [Brief description] 
        • Event 3: [Brief description]

        ## **⚡ ACTIONS**
        [Specific actions taken by the candidate]
        • Action 1: [Description]
        • Action 2: [Description]
        • Action 3: [Description]

        ## **🎊 RESULTS**
        [Outcomes and achievements mentioned]
        • Result 1: [Description with impact]
        • Result 2: [Description with impact]
        • Result 3: [Description with impact]

        ## **💡 SIGNIFICANCE**
        ### Competency Analysis:
        **Leadership**: [Analysis] - **Score: X/10**
        **Problem-Solving**: [Analysis] - **Score: X/10**  
        **Communication**: [Analysis] - **Score: X/10**
        **Teamwork**: [Analysis] - **Score: X/10**
        **Adaptability**: [Analysis] - **Score: X/10**

        ## **📈 OVERALL ASSESSMENT**
        **Top Strengths**: [List 3 key strengths]
        **Development Areas**: [List 2-3 improvement suggestions]
        **Overall Interview Score**: **X/10**
        **Hiring Recommendation**: **[STRONG HIRE/HIRE/MAYBE/PASS]**

        ## **🚀 IMPROVEMENT RECOMMENDATIONS**
        [Specific, actionable advice for future interviews]
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error generating feedback: {str(e)}"
    
    def _get_fallback_questions(self) -> List[str]:
        """Fallback questions if API fails."""
        return [
            "Tell me about a time when you had to lead a team through a difficult project. What was your approach?",
            "Describe a situation where you had to solve a complex problem with limited resources. How did you handle it?",
            "Can you share an example of when you had to work with a difficult team member or stakeholder?",
            "Tell me about a time when you had to adapt quickly to a significant change in your work environment.",
            "Describe a situation where you made a mistake. How did you handle it and what did you learn?",
            "Give me an example of when you had to influence others without having direct authority over them."
        ]

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

# Session State Management
def initialize_session_state():
    """Initialize all session state variables."""
    defaults = {
        'stage': 'upload',  # upload, details, interview, feedback
        'resume_text': "",
        'job_details': {},
        'questions': [],
        'current_question_idx': 0,
        'conversation': [],
        'feedback': "",
        'interview_completed': False,
        'gemini_client': None
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
        <p>Practice behavioral interviews with AI-powered feedback</p>
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

def render_sidebar():
    """Render sidebar with progress and controls."""
    with st.sidebar:
        st.title("📋 Interview Progress")
        
        # Current stage info
        stage_info = {
            'upload': "Upload your resume to get started",
            'details': "Provide job details for tailored questions",
            'interview': f"Question {st.session_state.current_question_idx + 1} of {len(st.session_state.questions)}" if st.session_state.questions else "Preparing interview questions...",
            'feedback': "Review your interview performance"
        }
        
        st.info(stage_info.get(st.session_state.stage, "Unknown stage"))
        
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
        progress = min(st.session_state.current_question_idx / len(st.session_state.questions), 1.0)
            st.progress(progress)
        
        st.divider()
        
        # Help section
        st.subheader("💡 Tips")
        if st.session_state.stage == 'upload':
            st.write("• Ensure your resume is up-to-date\n• Include relevant experience and skills\n• Supported formats: PDF, DOC, DOCX, TXT")
        elif st.session_state.stage == 'details':
            st.write("• Provide accurate job description\n• Be specific about requirements\n• Include years of experience needed")
        elif st.session_state.stage == 'interview':
            st.write("• Use the STAR method\n• Be specific with examples\n• Include measurable results\n• Take your time to think")
        elif st.session_state.stage == 'feedback':
            st.write("• Review all feedback sections\n• Focus on development areas\n• Practice recommended improvements")
        
        st.divider()
        
        # Restart option
        if st.button("🔄 Start New Interview", type="secondary"):
            for key in ['stage', 'resume_text', 'job_details', 'questions', 'current_question_idx', 'conversation', 'feedback', 'interview_completed']:
                if key in st.session_state:
                    del st.session_state[key]
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
    """Render job details collection stage."""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("📝 Job Details")
    st.write("Provide information about the position you're interviewing for. This helps us create tailored questions.")
    
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
                    'industry': industry
                }
                
                st.session_state.job_details = job_details
                
                # Generate questions
                with st.spinner("Generating personalized interview questions..."):
                    try:
                        questions = st.session_state.gemini_client.generate_questions(
                            st.session_state.resume_text,
                            job_details
                        )
                        st.session_state.questions = questions
                        st.session_state.stage = 'interview'
                        st.success("Questions generated successfully! Starting your interview...")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error generating questions: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_interview_stage():
    """Render interactive interview stage."""
    if not st.session_state.questions:
        st.error("No questions available. Please go back and regenerate questions.")
        return
    
    st.title("💬 Behavioral Interview")
    st.write(f"Question {st.session_state.current_question_idx + 1} of {len(st.session_state.questions)}")
    
    # Progress bar for interview
    progress = st.session_state.current_question_idx / len(st.session_state.questions)
    st.progress(progress)
    
    # Chat container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Display conversation history
    for msg in st.session_state.conversation:
        if msg['role'] == 'assistant':
            st.markdown(f'<div class="chat-message ai-message"><strong>Interviewer:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Current question or completion
    if st.session_state.current_question_idx < len(st.session_state.questions):
        current_question = st.session_state.questions[st.session_state.current_question_idx]
        
        # Show current question if not already in conversation
        if not st.session_state.conversation or st.session_state.conversation[-1]['content'] != current_question:
            st.markdown(f"""
            <div class="card">
                <h4>Current Question:</h4>
                <p style="font-size: 1.1em; font-weight: 500;">{current_question}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Add question to conversation
            st.session_state.conversation.append({
                'role': 'assistant',
                'content': current_question,
                'type': 'question'
            })
        
        # User response input
        with st.form(f"response_form_{st.session_state.current_question_idx}"):
            user_response = st.text_area(
                "Your Answer:",
                placeholder="Use the STAR method: Situation, Task, Action, Result...",
                height=150,
                key=f"response_{st.session_state.current_question_idx}"
            )
            
            submitted = st.form_submit_button("Submit Answer", type="primary")
            
            if submitted and user_response.strip():
                # Add user response to conversation
                st.session_state.conversation.append({
                    'role': 'user',
                    'content': user_response.strip()
                })
                
                # Get AI follow-up response
                with st.spinner("Analyzing your response..."):
                    try:
                        ai_response = st.session_state.gemini_client.get_interview_response(
                            current_question,
                            user_response,
                            st.session_state.conversation
                        )
                        
                        st.session_state.conversation.append({
                            'role': 'assistant',
                            'content': ai_response
                        })
                        
                        # Check if response indicates readiness for next question
                        if any(phrase in ai_response.lower() for phrase in ['next question', 'move on', 'ready for', 'great example']):
                            st.session_state.current_question_idx += 1
                        
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error getting response: {str(e)}")
        
        # Next question button (if AI hasn't automatically moved on)
        if st.session_state.conversation and st.session_state.conversation[-1]['role'] == 'assistant':
            col1, col2 = st.columns([1, 2])
            with col1:
                if st.button("Next Question", type="secondary"):
                    st.session_state.current_question_idx += 1
                    st.rerun()
    
    else:
        # Interview completed
        st.session_state.interview_completed = True
        st.markdown("""
        <div class="success-message">
            <h3>🎉 Interview Completed!</h3>
            <p>Great job! You've answered all the questions. Click below to get your detailed feedback.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Get My Feedback Report", type="primary"):
            with st.spinner("Generating your personalized feedback report..."):
                try:
                    feedback = st.session_state.gemini_client.generate_feedback(
                        st.session_state.conversation,
                        st.session_state.job_details
                    )
                    st.session_state.feedback = feedback
                    st.session_state.stage = 'feedback'
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating feedback: {str(e)}")

def render_feedback_stage():
    """Render feedback report stage."""
    st.title("📊 Interview Feedback Report")
    
    if not st.session_state.feedback:
        st.error("No feedback available. Please complete the interview first.")
        return
    
    # Display feedback report
    st.markdown('<div class="feedback-report">', unsafe_allow_html=True)
    st.markdown(st.session_state.feedback)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Download Report", type="secondary"):
            # Create downloadable report
            report_content = f"""
# AI Interview Simulator - Feedback Report

**Candidate:** Anonymous
**Position:** {st.session_state.job_details.get('job_title', 'N/A')}
**Company:** {st.session_state.job_details.get('company_name', 'N/A')}
**Date:** {time.strftime('%Y-%m-%d %H:%M')}

---

{st.session_state.feedback}

---

## Interview Conversation Log

"""
            for i, msg in enumerate(st.session_state.conversation):
                if msg['role'] == 'assistant':
                    report_content += f"\n**Interviewer:** {msg['content']}\n"
                else:
                    report_content += f"\n**Candidate:** {msg['content']}\n"
            
            st.download_button(
                label="Download Complete Report",
                data=report_content,
                file_name=f"interview_feedback_{time.strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown"
            )
    
    with col2:
        if st.button("🔄 Practice Again", type="primary"):
            st.session_state.stage = 'details'
            st.session_state.current_question_idx = 0
            st.session_state.conversation = []
            st.session_state.questions = []
            st.session_state.feedback = ""
            st.session_state.interview_completed = False
            st.rerun()
    
    with col3:
        if st.button("📝 New Interview", type="secondary"):
            for key in ['stage', 'resume_text', 'job_details', 'questions', 'current_question_idx', 'conversation', 'feedback', 'interview_completed']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    # Interview statistics
    st.divider()
    st.subheader("📈 Interview Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Questions Answered", len(st.session_state.questions))
    
    with col2:
        total_words = sum(len(msg['content'].split()) for msg in st.session_state.conversation if msg['role'] == 'user')
        st.metric("Total Words Spoken", total_words)
    
    with col3:
        avg_response_length = total_words // len([msg for msg in st.session_state.conversation if msg['role'] == 'user']) if st.session_state.conversation else 0
        st.metric("Avg Response Length", f"{avg_response_length} words")
    
    with col4:
        interview_duration = "~30 minutes"  # Estimated
        st.metric("Interview Duration", interview_duration)

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
        Practice makes perfect - Keep interviewing! 🚀
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
