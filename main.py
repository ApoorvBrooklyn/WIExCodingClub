import streamlit as st
import PyPDF2
from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ColdEmailGenerator:
    def __init__(self, api_key=None):
        """
        Initialize Groq client with multiple API key retrieval methods
        """
        # Priority order for API key retrieval:
        # 1. Passed parameter
        # 2. Environment variable
        # 3. Streamlit secrets
        # 4. Manual input through Streamlit

        if api_key:
            self.client = Groq(api_key=api_key)
        else:
            # Try environment variable
            env_key = os.getenv('GROQ_API_KEY')
            
            # Try Streamlit secrets
            if not env_key and hasattr(st.secrets, 'GROQ_API_KEY'):
                env_key = st.secrets.GROQ_API_KEY
            
            # If no key found, prompt user
            if not env_key:
                st.warning("Groq API Key not found. Please enter your API key.")
                env_key = st.text_input("Enter your Groq API Key", type="password")
            
            if env_key:
                self.client = Groq(api_key=env_key)
            else:
                st.error("No API key provided. Cannot initialize Groq client.")
                self.client = None

    def extract_text_from_pdf(self, pdf_file):
        """
        Extract text from uploaded PDF resume
        """
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            st.error(f"Error reading PDF: {e}")
            return None

    def generate_cold_email(self, job_description, resume_text):
        """
        Generate a personalized cold email using Groq API
        """
        if not self.client:
            st.error("Groq client not initialized. Cannot generate email.")
            return None

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": """You are a professional email writer specializing in cold outreach for job applications. 
                        Create a personalized, concise, and compelling cold email that:
                        1. Demonstrates knowledge of the company and role
                        2. Highlights relevant skills from the resume
                        3. Shows genuine interest in the position
                        4. Maintains a professional yet warm tone
                        5. Keeps the email to 3-4 paragraphs max"""
                    },
                    {
                        "role": "user",
                        "content": f"Job Description:\n{job_description}\n\nMy Resume:\n{resume_text}"
                    }
                ],
                model="llama3-70b-8192",
                max_tokens=500,
                temperature=0.7
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            st.error(f"Error generating email: {e}")
            return None

def main():
    st.title("🚀 Cold Email Generator for Job Applications")
    
    # Sidebar for instructions and API key input
    st.sidebar.header("Configuration")
    
    # Optional manual API key input
    manual_api_key = st.sidebar.text_input("Groq API Key (optional)", type="password")
    
    # Instructions
    st.sidebar.header("How to Use")
    st.sidebar.info("""
    1. Set up Groq API Key:
       - Via .env file
       - Via Streamlit secrets
       - Manual input
    2. Upload your PDF resume
    3. Paste the job description
    4. Generate a personalized cold email
    """)

    # Initialize email generator
    email_generator = ColdEmailGenerator(api_key=manual_api_key)

    # Resume upload
    st.header("Upload Your Resume")
    uploaded_resume = st.file_uploader("Choose a PDF file", type="pdf")

    # Job description input
    st.header("Job Description")
    job_description = st.text_area("Paste the full job description here", height=200)

    # Generate button
    if st.button("Generate Cold Email"):
        # Validate inputs
        if not uploaded_resume:
            st.warning("Please upload your resume")
            return
        
        if not job_description:
            st.warning("Please paste the job description")
            return

        # Extract resume text
        resume_text = email_generator.extract_text_from_pdf(uploaded_resume)
        
        if resume_text:
            # Generate email
            generated_email = email_generator.generate_cold_email(job_description, resume_text)
            
            if generated_email:
                st.header("Generated Cold Email")
                st.write(generated_email)
                
                # Copy to clipboard button
                st.button("Copy to Clipboard")

# Requirements and setup notes
st.sidebar.markdown("""
### Dependencies
```bash
pip install streamlit groq PyPDF2 python-dotenv
```

### API Key Configuration
1. `.env` file:
   ```
   GROQ_API_KEY=your_groq_api_key
   ```
2. Streamlit Secrets
3. Manual input in sidebar
""")

if __name__ == "__main__":
    main()