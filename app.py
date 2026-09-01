"""
AI Career Roadmap Generator
----------------------------
A Streamlit application that uses Google's Gemini API to generate
personalized, phase-by-phase career roadmaps based on a user's
current education, target role, skill level, and time horizon.

Run with:
    streamlit run app.py

Requires:
    pip install streamlit google-genai
"""

import streamlit as st
from datetime import datetime

# ---------------------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Career Roadmap Generator",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS Styling
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.4rem;
        font-weight: 800;
        color: #1f2937;
        margin-bottom: 0rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #6b7280;
        margin-bottom: 1.5rem;
    }
    .roadmap-container {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.75rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        margin-bottom: 1.25rem;
    }
    .metric-box {
        background-color: #f9fafb;
        border-radius: 10px;
        padding: 0.75rem 1rem;
        border: 1px solid #eef0f2;
    }
    div.stButton > button {
        background-color: #2563eb;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        border: none;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #1d4ed8;
        color: white;
    }
    div[data-testid="stDownloadButton"] > button {
        background-color: #059669;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        border: none;
        width: 100%;
    }
    div[data-testid="stDownloadButton"] > button:hover {
        background-color: #047857;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------------------------
if "roadmap_text" not in st.session_state:
    st.session_state.roadmap_text = None
if "generation_meta" not in st.session_state:
    st.session_state.generation_meta = {}

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown('<p class="main-header">🧭 AI Career Roadmap Generator</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">Get a personalized, phase-by-phase career plan '
    'powered by Google Gemini — tailored to your background and goals.</p>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar — Inputs
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")

    api_key = st.text_input(
        "Gemini API Key",
        type="password",
        placeholder="Enter your Google Gemini API key",
        help="Your key is used only for this session and is never stored.",
    )

    st.markdown("---")
    st.header("👤 Your Profile")

    degree = st.text_input(
        "Current Degree / Major",
        placeholder="e.g., Electrical Engineering, Computer Science",
    )

    target_role = st.text_input(
        "Target Job Role",
        placeholder="e.g., IoT Engineer, Data Scientist, Embedded Systems Developer",
    )

    skill_level = st.selectbox(
        "Current Skill Level",
        options=["Beginner", "Intermediate", "Advanced"],
        index=0,
    )

    time_horizon = st.selectbox(
        "Time Horizon",
        options=["3 Months", "6 Months", "1 Year", "2 Years"],
        index=1,
    )

    st.markdown("---")
    generate_clicked = st.button("🚀 Generate Roadmap", use_container_width=True)

# ---------------------------------------------------------------------------
# Prompt Construction
# ---------------------------------------------------------------------------
def build_prompt(degree: str, target_role: str, skill_level: str, time_horizon: str) -> str:
    """Builds a structured prompt instructing Gemini to output a career roadmap."""
    return f"""
You are an expert career coach and technical mentor specializing in engineering
and technology careers. Generate a detailed, actionable, and realistic career
roadmap in well-formatted Markdown for the following person:

- Current Degree / Major: {degree}
- Target Job Role: {target_role}
- Current Skill Level: {skill_level}
- Time Horizon: {time_horizon}

Structure your response EXACTLY using the following Markdown sections and headers:

## 📌 Overview
A short 2-3 sentence summary of the plan and how it fits the {time_horizon} timeframe.

## 🗺️ Phase-by-Phase Roadmap

### Phase 1: Foundations
- Bullet points of specific topics, concepts, and foundational skills to learn.
- Include estimated time allocation for this phase.

### Phase 2: Core Skills
- Bullet points of the core technical skills, tools, and frameworks specific to {target_role}.
- Include estimated time allocation for this phase.

### Phase 3: Projects
- Bullet points describing hands-on project work and skill consolidation.
- Include estimated time allocation for this phase.

### Phase 4: Job Hunt
- Bullet points on resume building, portfolio polishing, networking, and interview prep.
- Include estimated time allocation for this phase.

## 🛠️ Recommended Tools, Frameworks & Certifications
- A bullet list of specific tools/frameworks to learn.
- A bullet list of relevant certifications (with issuing body) worth pursuing.

## 💡 3 Real-World Portfolio Project Ideas
For each project, use this exact sub-format:

### Project 1: [Project Title]
- **Goal:** ...
- **Key Skills Demonstrated:** ...
- **Tech Stack:** ...

### Project 2: [Project Title]
- **Goal:** ...
- **Key Skills Demonstrated:** ...
- **Tech Stack:** ...

### Project 3: [Project Title]
- **Goal:** ...
- **Key Skills Demonstrated:** ...
- **Tech Stack:** ...

## ✅ Success Metrics
A short bullet list of 4-6 measurable milestones the person can use to track
their progress toward becoming a {target_role} within {time_horizon}.

Keep the tone motivating but realistic, and tailor every recommendation
specifically to someone transitioning from a {degree} background into a
{target_role} role at a {skill_level} skill level.
""".strip()


# ---------------------------------------------------------------------------
# Gemini API Call
# ---------------------------------------------------------------------------
def generate_roadmap(api_key: str, prompt: str) -> str:
    """Calls the Gemini API and returns the generated roadmap text."""
    from google import genai

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )
    return response.text


# ---------------------------------------------------------------------------
# Helper: Parse simple metrics from the roadmap for the summary chips
# ---------------------------------------------------------------------------
def extract_section(markdown_text: str, header: str, next_headers: list) -> str:
    """Extracts the text of a section between `header` and the next matching header."""
    lines = markdown_text.splitlines()
    start_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith(header):
            start_idx = i + 1
            break
    if start_idx is None:
        return ""

    end_idx = len(lines)
    for j in range(start_idx, len(lines)):
        stripped = lines[j].strip()
        if any(stripped.startswith(h) for h in next_headers):
            end_idx = j
            break

    return "\n".join(lines[start_idx:end_idx]).strip()


# ---------------------------------------------------------------------------
# Main Action — Generate Button Logic
# ---------------------------------------------------------------------------
if generate_clicked:
    if not api_key:
        st.error("⚠️ Please enter your Gemini API Key in the sidebar to continue.")
    elif not degree or not target_role:
        st.error("⚠️ Please fill in both your Degree/Major and Target Job Role.")
    else:
        prompt = build_prompt(degree, target_role, skill_level, time_horizon)
        with st.spinner("🤖 Generating your personalized career roadmap..."):
            try:
                result_text = generate_roadmap(api_key, prompt)
                st.session_state.roadmap_text = result_text
                st.session_state.generation_meta = {
                    "degree": degree,
                    "target_role": target_role,
                    "skill_level": skill_level,
                    "time_horizon": time_horizon,
                    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }
                st.success("✅ Roadmap generated successfully!")
            except Exception as e:
                st.error(f"❌ Failed to generate roadmap: {e}")

# ---------------------------------------------------------------------------
# Display Output
# ---------------------------------------------------------------------------
if st.session_state.roadmap_text:
    meta = st.session_state.generation_meta
    roadmap = st.session_state.roadmap_text

    # Summary metric chips
    st.markdown("### 📊 Roadmap Summary")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f'<div class="metric-box"><b>🎓 Background</b><br>{meta.get("degree", "-")}</div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f'<div class="metric-box"><b>🎯 Target Role</b><br>{meta.get("target_role", "-")}</div>',
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f'<div class="metric-box"><b>📈 Skill Level</b><br>{meta.get("skill_level", "-")}</div>',
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f'<div class="metric-box"><b>⏱️ Time Horizon</b><br>{meta.get("time_horizon", "-")}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Full roadmap in a styled container
    st.markdown("### 🗺️ Your Personalized Roadmap")
    st.markdown(f'<div class="roadmap-container">{roadmap}</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Expandable breakdown by phase
    st.markdown("### 🔍 Explore by Section")

    phase_headers = [
        "### Phase 1: Foundations",
        "### Phase 2: Core Skills",
        "### Phase 3: Projects",
        "### Phase 4: Job Hunt",
    ]
    tools_header = "## 🛠️ Recommended Tools, Frameworks & Certifications"
    projects_header = "## 💡 3 Real-World Portfolio Project Ideas"
    metrics_header = "## ✅ Success Metrics"

    all_headers = phase_headers + [tools_header, projects_header, metrics_header, "## "]

    with st.expander("Phase 1: Foundations", expanded=False):
        content = extract_section(roadmap, "### Phase 1: Foundations", phase_headers[1:] + [tools_header])
        st.markdown(content if content else "_Section not found in response._")

    with st.expander("Phase 2: Core Skills", expanded=False):
        content = extract_section(roadmap, "### Phase 2: Core Skills", phase_headers[2:] + [tools_header])
        st.markdown(content if content else "_Section not found in response._")

    with st.expander("Phase 3: Projects", expanded=False):
        content = extract_section(roadmap, "### Phase 3: Projects", phase_headers[3:] + [tools_header])
        st.markdown(content if content else "_Section not found in response._")

    with st.expander("Phase 4: Job Hunt", expanded=False):
        content = extract_section(roadmap, "### Phase 4: Job Hunt", [tools_header])
        st.markdown(content if content else "_Section not found in response._")

    with st.expander("🛠️ Tools, Frameworks & Certifications", expanded=False):
        content = extract_section(roadmap, tools_header, [projects_header])
        st.markdown(content if content else "_Section not found in response._")

    with st.expander("💡 Portfolio Project Ideas", expanded=False):
        content = extract_section(roadmap, projects_header, [metrics_header])
        st.markdown(content if content else "_Section not found in response._")

    with st.expander("✅ Success Metrics", expanded=False):
        content = extract_section(roadmap, metrics_header, ["## ZZZ_END_MARKER"])
        st.markdown(content if content else "_Section not found in response._")

    st.markdown("---")

    # Download button
    file_content = (
        f"AI CAREER ROADMAP\n"
        f"Generated: {meta.get('generated_at', '')}\n"
        f"Background: {meta.get('degree', '')}\n"
        f"Target Role: {meta.get('target_role', '')}\n"
        f"Skill Level: {meta.get('skill_level', '')}\n"
        f"Time Horizon: {meta.get('time_horizon', '')}\n"
        f"{'-' * 60}\n\n"
        f"{roadmap}"
    )

    safe_role = "".join(c if c.isalnum() else "_" for c in meta.get("target_role", "roadmap"))
    filename = f"career_roadmap_{safe_role}.md"

    st.download_button(
        label="📥 Download Roadmap (.md)",
        data=file_content,
        file_name=filename,
        mime="text/markdown",
        use_container_width=True,
    )

else:
    st.info(
        "👈 Fill in your details in the sidebar and click **Generate Roadmap** "
        "to get started."
    )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.caption(
    "Built with Streamlit & Google Gemini · Your API key is used only "
    "for this session and is never stored or logged."
)
