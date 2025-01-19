import streamlit as st
from  datetime import datetime, date
from pathlib import Path

from data_access import load_offer, load_cv_data, save_cv_data

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


def display_user_form(username, data):
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

    #Education
    with st.expander("Education"):
        EduDeleteButton = []
        EduDataForm = []
        EduCount = 0

        if data["profile"].get("education"):
            EduData = data["profile"]["education"]
            for x,edu in enumerate(EduData):
                EduDataForm.append(make_edu_form(edu, x))
                EduDeleteButton.append(st.button(f"Delete Education {x + 1}"))
            EduCount = len(EduDataForm)
        else:
            EduDataForm.append(make_edu_form({}, 0))
            EduDeleteButton.append(st.button(f"Delete Education {1}"))
        if st.button("Add New Education"):
            EduDataForm.append(make_edu_form({}, EduCount))
            EduDeleteButton.append(st.button(f"Delete Education {EduCount + 1}"))
        for counter,button in enumerate(EduDeleteButton):
            if button:
                data["profile"]["education"].pop(counter)
                save_cv_data(username, data)
                st.rerun()

    # Tech Stack
    with st.expander("Tech Stack"):
        tech_stack = st.text_area("Technical Skills (comma-separated)", ", ".join(data["profile"].get("tech_stack", [])))
    
    # Soft Skills
    with st.expander("Soft Skills"):
        soft_stack = st.text_area("Soft Skills (comma-separated)", ", ".join(data["profile"].get("soft_stack", [])))

    # Work Experience
    with st.expander("Work Experience"):
        WorkDeleteButton = []
        WorkDataForm = []
        WorkCount = 0

        if data["profile"].get("work_experience"):
            WorkData = data["profile"]["work_experience"]
            for x,work in enumerate(WorkData):
                WorkDataForm.append(make_work_form(work, x))
                WorkDeleteButton.append(st.button(f"Delete Work Experience {x + 1}"))
            WorkCount = len(WorkDataForm)
        else:
            WorkDataForm.append(make_work_form({}, 0))
            WorkDeleteButton.append(st.button(f"Delete Work Experience {1}"))
        if st.button("Add New Work Experience"):
            WorkDataForm.append(make_work_form({}, WorkCount))
            WorkDeleteButton.append(st.button(f"Delete Work Experience {WorkCount + 1}"))
        for counter,button in enumerate(WorkDeleteButton):
            if button:
                data["profile"]["work_experience"].pop(counter)
                save_cv_data(username, data)
                st.rerun()



    # Projects
    with st.expander("Projects"):
        ProjDeleteButton = []
        ProjDataForm = []
        ProjCount = 0

        if data["profile"].get("projects"):
            ProjData = data["profile"]["projects"]
            for x,project in enumerate(ProjData):
                ProjDataForm.append(make_project_form(project, x))
                ProjDeleteButton.append(st.button(f"Delete Project {x + 1}"))
            ProjCount = len(ProjDataForm)
        else:
            ProjDataForm.append(make_project_form({}, 0))
            ProjDeleteButton.append(st.button(f"Delete Project {1}"))
        if st.button("Add New Project"):
            ProjDataForm.append(make_project_form({}, ProjCount))
            ProjDeleteButton.append(st.button(f"Delete Project {ProjCount + 1}"))
        for counter,button in enumerate(ProjDeleteButton):
            if button:
                data["profile"]["projects"].pop(counter)
                save_cv_data(username, data)
                st.rerun()
                
    # Certifications
    with st.expander("Certifications"):
        CertDeleteButton = []
        CertDataForm = []
        CertCount = 0

        if data["profile"].get("certifications"):
            CertData = data["profile"]["certifications"]
            for x,cert in enumerate(CertData):
                CertDataForm.append(make_cert_form(cert, x))
                CertDeleteButton.append(st.button(f"Delete Certification {x + 1}"))
            CertCount = len(CertDataForm)
        else:
            CertDataForm.append(make_cert_form({}, 0))
            CertDeleteButton.append(st.button(f"Delete Certification {1}"))
        if st.button("Add New Certification"):
            CertDataForm.append(make_cert_form({}, CertCount))
            CertDeleteButton.append(st.button(f"Delete Certification {CertCount + 1}"))
        for counter,button in enumerate(CertDeleteButton):
            if button:
                data["profile"]["certifications"].pop(counter)
                save_cv_data(username, data)
                st.rerun()

    # Languages
    with st.expander("Languages"):
        LangDeleteButton = []
        LangDataForm = []
        LangCount = 0

        if data["profile"].get("languages"):
            LangData = data["profile"]["languages"]
            for x,lang in enumerate(LangData):
                LangDataForm.append(make_lang_form(lang, x))
                LangDeleteButton.append(st.button(f"Delete Language {x + 1}"))
            LangCount = len(LangDataForm)
        else:
            LangDataForm.append(make_lang_form({}, 0))
            LangDeleteButton.append(st.button(f"Delete Language {1}"))
        if st.button("Add New Language"):
            LangDataForm.append(make_lang_form({}, LangCount))
            LangDeleteButton.append(st.button(f"Delete Language {LangCount + 1}"))
        for counter,button in enumerate(LangDeleteButton):
            if button:
                data["profile"]["languages"].pop(counter)
                save_cv_data(username, data)
                st.rerun()
    
    # About Me
    with st.expander("About Me"):
        about_me = st.text_area("About Me", data["profile"].get("about_me", ""))

    #if st.button("Submit"):
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
            "education": get_edu_form(EduDataForm),
            "work_experience": get_work_data(WorkDataForm),
            "projects": get_project_data(ProjDataForm),
            "certifications": get_certification_data(CertDataForm),
            "languages": get_lang_data(LangDataForm),
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

def make_work_form(work, x):
    work_company = st.text_input(f"Company {x + 1}", work.get("company", ""))
    work_position = st.text_input(f"Position {x + 1}", work.get("position", ""))
    work_start_date = st.date_input(f"Start Date {x + 1}", key=f"work_start_date_{x}", value=parse_data(work.get("start_date", '')))
    work_end_date = st.date_input(f"End Date {x + 1}", key=f"work_end_date_{x}", value=parse_data(work.get("end_date", '')))
    work_description = st.text_area(f"Description {x + 1}", work.get("description", ""))
    return {
        "company": work_company,
        "position": work_position,
        "start_date": work_start_date,
        "end_date": work_end_date,
        "description": work_description
    }

def make_edu_form(education, x):
    institution = st.text_input(f"Institution {x + 1}", education.get("institution", ""))
    degree = st.text_input(f"Degree {x + 1}", education.get("degree", ""))
    field_of_study = st.text_input(f"Field of Study {x + 1}", education.get("field_of_study", ""))
    specialization = st.text_input(f"Specialization {x + 1}", education.get("specialization", ""))
    start_date_edu = st.date_input(f"Start Date {x + 1}", key=f"edu_start_{x}", value=parse_data(education.get("start_date", '')))
    end_date_edu = st.date_input(f"End Date {x + 1}", key=f"edu_end_{x}", value=parse_data(education.get("end_date", '')))
    return {
        "institution": institution,
        "degree": degree,
        "field_of_study": field_of_study,
        "specialization": specialization,
        "start_date": start_date_edu,
        "end_date": end_date_edu
    }


def make_cert_form(certification, x):
    cert_name = st.text_input(f"Certification Name {x + 1}", certification.get("name", ""))
    cert_authority = st.text_input(f"Certification Authority {x + 1}", certification.get("authority", ""))
    cert_date = st.date_input(f"Certification Date {x + 1}", key=f"cert_date_{x}", value=parse_data(certification.get("date", '')))
    cert_description = st.text_area(f"Certification Description {x + 1}", certification.get("description", ""))
    return {
        "name": cert_name,
        "authority": cert_authority,
        "date": cert_date,
        "description": cert_description
    }

def make_lang_form(language, x):
    lang_name = st.text_input(f"Language {x + 1}", language.get("language", ""))
    lang_proficiency = st.text_input(f"Proficiency {x + 1}", language.get("proficiency", ""))
    return {
        "language": lang_name,
        "proficiency": lang_proficiency
    }

def get_work_data(workDataForm):
    WorkData = []
    for work in workDataForm:
        WorkData.append({
            "company": work.get("company", ""),
            "position": work.get("position", ""),
            "start_date": work.get("start_date", "").strftime("%Y-%m-%d"),
            "end_date": work.get("end_date", "").strftime("%Y-%m-%d"),
            "description": work.get("description", "")
    })
    return WorkData

def get_edu_form(eduDataForm):
    EduData = []
    for edu in eduDataForm:
        EduData.append({
            "institution": edu.get("institution", ""),
            "degree": edu.get("degree", ""),
            "field_of_study": edu.get("field_of_study", ""),
            "specialization": edu.get("specialization", ""),
            "start_date": edu.get("start_date", "").strftime("%Y-%m-%d"),
            "end_date": edu.get("end_date", "").strftime("%Y-%m-%d")
    })
    return EduData

def get_lang_data(langDataForm):
    LangData = []
    for lang in langDataForm:
        LangData.append({
            "language": lang.get("language", ""),
            "proficiency": lang.get("proficiency", "")
    })
    return LangData

def get_certification_data(certDataForm):
    CertData = []
    for cert in certDataForm:
        CertData.append({
            "name": cert.get("name", ""),
            "authority": cert.get("authority", ""),
            "date": cert.get("date", "").strftime("%Y-%m-%d"),
            "description": cert.get("description", "")
    })
    print(CertData)
    return CertData

def get_project_data(projectDataForm):
    ProjData = []
    for project in projectDataForm:
        ProjData.append({
            "name": project.get("name", ""),
            "description": project.get("description", ""),
            "tech_stack": project.get("tech_stack", []),
            "github": project.get("github", ""),
            "demo": project.get("demo", "")
    })
    return ProjData

def parse_data(dateGiven):
    if dateGiven is None or dateGiven == '':
        return date(2000, 1, 1)
    else:
        return datetime.strptime(dateGiven, "%Y-%m-%d")

    