import streamlit as st

def render_ats_templates(ats_score):
    st.markdown("## 📄 Improve Your ATS Score")

    if ats_score < 50:
        st.error("Low ATS score - improve resume format")
    elif ats_score < 75:
        st.warning("Good ATS score - can be improved")
    else:
        st.success("Excellent ATS score")

    st.markdown("---")

    st.subheader("🔹 Simple ATS Resume")

    st.write("Best for freshers. Clean format, no tables.")

    st.download_button(
        "Download Template",
        data="""NAME
Email | Phone | LinkedIn

SKILLS:
Python, SQL, Excel

EDUCATION:
Your Degree

PROJECTS:
- Project 1
- Project 2
""",
        file_name="ATS_Resume.txt"
    )