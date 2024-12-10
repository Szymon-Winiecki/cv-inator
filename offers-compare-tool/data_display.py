import streamlit as st
from  datetime import datetime, date
from pathlib import Path

from data_access import load_offer, load_cv_data

def display_job_offer(offer_record):

    offer_id, offer_details = offer_record
    offer_path = Path(offer_details.get("path", ""))

    offer = load_offer(offer_path)

    if offer is None:
        st.write(f"Error loading offer {offer_id}, {offer_details}")
        return
    
    timestamp = offer.get("timestamp", "")
    timestamp = datetime.fromisoformat(timestamp.replace("Z", "")).strftime("%Y-%m-%d %H:%M:%S")
    source_url = offer.get("source", "#")

    offer = offer.get("offer", {})

    st.subheader(f"{offer.get('offer_title', 'Unknown Position')} at {offer.get('company', 'Unknown Company')}")
    # Display job details
    st.write(f"**Location:** {offer.get('location', 'Not specified')}")
    st.write(f"**Salary:** {offer.get('salary', 'Not specified')}")
    st.write(f"**Contract Type:** {offer.get('contract', 'Not specified')}")
    st.write(f"**Experience Level:** {offer.get('experience', 'Not specified')}")
    st.write(f"**Expected Technologies:** {offer.get('expected_technologies', 'Not specified')}")
    st.write(f"**Optional Technologies:** {offer.get('optional_technologies', 'Not specified')}")
    st.write(f"**Posted on:** {timestamp}")

    # Display job offer content and responsibilities
    st.subheader("Job Description")
    st.write(offer.get("offer_content", "No description available"))

    # Display application link
    st.subheader("Original offer Link")
    st.write(f"[Apply here]({source_url})")


def display_user_form(username):
    data = load_cv_data(username)
    # Personal Info
    with st.expander("Personal Information"):
        personal_info = data["profile"].get("personal_info", {})
        name = st.text_input("Name", personal_info.get("name", ""))
        title = st.text_input("Title", personal_info.get("title", ""))
        location = st.text_input("Location", personal_info.get("location", ""))
        email = st.text_input("Email", personal_info.get("email", ""))
        phone = st.text_input("Phone", personal_info.get("phone", ""))
        linkedin = st.text_input("LinkedIn", personal_info.get("linkedin", ""))
        github = st.text_input("GitHub", personal_info.get("github", ""))
    
    with st.expander("Education"):
        if data["profile"].get("education"):
            education = data["profile"]["education"][0]
        else:
            education = {}
        institution = st.text_input("Institution", education.get("institution", ""))
        degree = st.text_input("Degree", education.get("degree", ""))
        field_of_study = st.text_input("Field of Study", education.get("field_of_study", ""))
        specialization = st.text_input("Specialization", education.get("specialization", ""))
        start_date_edu = st.date_input("Start Date", key="edu_start", value=parse_data(education.get("start_date", '')))
        end_date_edu = st.date_input("End Date", key="edu_end", value=parse_data(education.get("end_date", '')))

    # Tech Stack
    with st.expander("Tech Stack"):
        tech_stack = st.text_area("Technical Skills (comma-separated)", ", ".join(data["profile"].get("tech_stack", [])))
    
    # Soft Skills
    with st.expander("Soft Skills"):
        soft_stack = st.text_area("Soft Skills (comma-separated)", ", ".join(data["profile"].get("soft_stack", [])))

    # Work Experience
    with st.expander("Work Experience"):
        if data["profile"].get("work_experience"):
            work_experience = data["profile"]["work_experience"][0]
        else:
            work_experience = {}
        company = st.text_input("Company", work_experience.get("company", ""))
        position = st.text_input("Position", work_experience.get("position", ""))
        start_date_work = st.date_input("Start Date (Work)", key="work_start", value=parse_data(work_experience.get("start_date", '')))
        end_date_work = st.date_input("End Date (Work)", key="work_end", value=parse_data(work_experience.get("end_date", '')))
        description = st.text_area("Description", work_experience.get("description", ""))
        if st.button("Add New Work Experience"):
            # Dodajemy pusty słownik na nowe doświadczenie
            st.session_state.work_experience.append({
                "company": "",
                "position": "",
                "start_date": date(2000, 1, 1),
                "end_date": date(2000, 1, 1),
                "description": "",
            })
    
    # Projects
    with st.expander("Projects"):
        if data["profile"].get("projects"):
            projectData = data["profile"]["projects"]
            for x,project in enumerate(projectData):
                projectData[x] = make_project_form(project, x)

        else:
            project = {}
            projectData = []
            projectData[0] = make_project_form(project, 1)
    
    # Certifications
    with st.expander("Certifications"):
        if data["profile"].get("certifications"):
            certification = data["profile"]["certifications"][0]
        else:
            certification = {}
        certification_name = st.text_input("Certification Name", certification.get("name", ""))
        certification_authority = st.text_input("Certification Authority", certification.get("authority", ""))
        certification_date = st.date_input("Certification Date", key="cert_date", value=parse_data(certification.get("date", '')))
        certification_description = st.text_area("Certification Description", certification.get("description", ""))
    
    # Languages
    with st.expander("Languages"):
        if data["profile"].get("languages"):
            language_info = data["profile"]["languages"][0]
        else:
            language_info = {}
        language = st.text_input("Language", language_info.get("language", ""))
        proficiency = st.text_input("Proficiency", language_info.get("proficiency", ""))
    
    # About Me
    with st.expander("About Me"):
        about_me = st.text_area("About Me", data["profile"].get("about_me", ""))

    if st.button("Submit"):
        profile_data = {
            "profile": {
                "personal_info": {
                    "name": name,
                    "title": title,
                    "location": location,
                    "email": email,
                    "phone": phone,
                    "linkedin": linkedin,
                    "github": github
                },
                "tech_stack": tech_stack.split(", "),
                "soft_stack": soft_stack.split(", "),
                "education": [{
                    "institution": institution,
                    "degree": degree,
                    "field_of_study": field_of_study,
                    "specialization": specialization,
                    "start_date": str(start_date_edu),
                    "end_date": str(end_date_edu)
                }],
                "work_experience": [{
                    "company": company,
                    "position": position,
                    "start_date": str(start_date_work),
                    "end_date": str(end_date_work),
                    "description": description
                }],
                "projects": get_project_data(projectData),
                "certifications": [{
                    "name": certification_name,
                    "authority": certification_authority,
                    "date": str(certification_date),
                    "description": certification_description
                }],
                "languages": [{
                    "language": language,
                    "proficiency": proficiency
                }],
                "about_me": about_me
            }
        }
        return profile_data

def make_project_form(project, x):
    project_name = st.text_input(f"Project Name {x + 1}", project.get("name", ""))
    project_description = st.text_area(f"Project Description {x + 1}", project.get("description", ""))
    project_tech_stack = st.text_area(f"Project Tech Stack (comma-separated) {x + 1}", ", ".join(project.get("tech_stack", [])))
    project_github = st.text_input(f"Project GitHub {x + 1}", project.get("github", ""))
    project_demo = st.text_input(f"Project Demo {x + 1}", project.get("demo", ""))
    return {
        "name": project_name,
        "description": project_description,
        "tech_stack": project_tech_stack.split(", "),
        "github": project_github,
        "demo": project_demo
    }

def get_project_data(projectData):
    data = []
    for project in projectData:
        data.append({
            "name": project.get("name", ""),
            "description": project.get("description", ""),
            "tech_stack": project.get("tech_stack", []),
            "github": project.get("github", ""),
            "demo": project.get("demo", "")
    })
    return data

def parse_data(dateGiven):
    if dateGiven is None or dateGiven == '':
        return date(2000, 1, 1)
    else:
        return datetime.strptime(dateGiven, "%Y-%m-%d")

    