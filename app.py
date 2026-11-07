import os
import streamlit as st
from dotenv import load_dotenv
from tavily import TavilyClient
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# Load API credentials from .env file
load_dotenv()

TAVILY_KEY = os.getenv("TAVILY_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# Enforce clean structured output from the LLM
class DetectionReport(BaseModel):
    verdict: str = Field(description="Must be exactly 'REAL', 'FAKE', or 'UNVERIFIED / MIXED'")
    confidence_score: int = Field(description="Confidence percentage from 0 to 100 based on search alignment")
    explanation: str = Field(description="A concise summary detailing why this news is real or fake based on sources.")
    red_flags: list[str] = Field(description="List of logical fallacies, clickbait language, or missing validation flags.")

def search_live_web(headline: str) -> str:
    """Queries live internet context via Tavily API including raw text content."""
    try:
        tavily = TavilyClient(api_key=TAVILY_KEY)
        # Search specifically for news content and fact checks
        search_query = f'"{headline}" fact check news sources'
        response = tavily.search(query=search_query, max_results=5, include_answer=True)
        
        # Compile snippets into a unified block of context
        context_blocks = []
        if response.get("answer"):
            context_blocks.append(f"Summary: {response['answer']}")
            
        for idx, result in enumerate(response.get("results", []), 1):
            context_blocks.append(
                f"Source [{idx}]: {result.get('title')}\n"
                f"URL: {result.get('url')}\n"
                f"Snippet: {result.get('content')}\n"
            )
        return "\n---\n".join(context_blocks)
    except Exception as e:
        st.error(f"Search API Error: {str(e)}")
        return ""

def analyze_veracity(headline: str, web_context: str) -> DetectionReport:
    """Passes live context to Gemini Flash Lite for zero-shot text classification analysis."""
    client = genai.Client(api_key=GEMINI_KEY)
    
    # We add highly descriptive structural instructions to assist the Lite model's reasoning
    prompt = f"""
    You are an expert investigative fact-checker. Analyze the provided headline against the live internet search context.
    
    CRITICAL STRUCTURE INSTRUCTION: You must strictly return a valid JSON payload matching the requested schema. Do not include markdown formatting like ```json or trailing text.
    
    Headline to evaluate: "{headline}"
    
    Live Internet Search Context:
    {web_context}
    
    Instructions:
    1. Cross-reference the headline with the details found in the search context.
    2. If reliable news sources validate it, mark it 'REAL'. If credible sources explicitly debunk it or it is structurally missing validation from any mainstream reporting, mark it 'FAKE'. If evidence is conflicting, mixed, or too fresh to tell, mark it 'UNVERIFIED / MIXED'.
    3. Calculate an accurate confidence score based on the clarity and strength of your evidence.
    """
    
    # Execute structural reasoning using Gemini 3.5 Flash Lite
    response = client.models.generate_content(
        model='gemini-3.5-flash-lite',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=DetectionReport
        ),
    )
    # Return structured object parsing the raw text response
    return DetectionReport.model_validate_json(response.text)

# --- Streamlit Web App Interface Framework ---
st.set_page_config(page_title="Real-Time Fake News Detector", layout="centered")

st.title("Real-Time Fake News Detector")
st.markdown("Verify the authenticity of any current breaking news headline against the live web using AI.")

headline_input = st.text_input("Enter News Headline or Claim:", placeholder="e.g., NASA confirms asteroid will hit Earth tomorrow...")

if st.button("Analyze Authenticity", type="primary"):
    if not headline_input.strip():
        st.warning("Please enter a valid headline first.")
    elif not TAVILY_KEY or not GEMINI_KEY:
        st.error("Missing API Keys! Please ensure your `.env` file contains your functional keys.")
    else:
        with st.spinner("Scouring live internet networks & cross-referencing sources..."):
            # Step 1: Scrape the active internet context
            live_context = search_live_web(headline_input)
            
            if not live_context:
                st.error("Unable to gather context from the web. Try a different variation of the headline.")
            else:
                try:
                    # Step 2: Use AI to analyze the context
                    report = analyze_veracity(headline_input, live_context)
                    
                    # Step 3: Render visual metrics
                    st.subheader("Analysis Verdict")
                    
                    if report.verdict == "REAL":
                        st.success(f"Verdict: **{report.verdict}**")
                    elif report.verdict == "FAKE":
                        st.error(f"Verdict: **{report.verdict}**")
                    else:
                        st.warning(f"Verdict: **{report.verdict}**")
                        
                    st.metric(label="System Confidence Score", value=f"{report.confidence_score}%")
                    
                    st.markdown(" Fact-Check Breakdown")
                    st.write(report.explanation)
                    
                    if report.red_flags:
                        st.markdown(" Identified Red Flags")
                        for flag in report.red_flags:
                            st.markdown(f"- {flag}")
                            
                    st.markdown("---")
                    st.info("Verification complete. The analysis is generated by comparing the claim to real-time search context indexing verified domains.")
                except Exception as e:
                    st.error(f"An error occurred while parsing the AI response: {str(e)}")
                    st.info("The Lite model might have struggled with the structure. Try running the headline again.")
