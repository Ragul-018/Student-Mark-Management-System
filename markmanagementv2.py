import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
from io import BytesIO

# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "student_roll_number" not in st.session_state:
    st.session_state.student_roll_number = None
if "master_df" not in st.session_state:
    st.session_state.master_df = pd.DataFrame(columns=["Roll Number", "Name", "Principles of AI", "Software Construction", "Computer Networks", "Object Oriented Programming Using Java", "Mathematics"])

# Function to calculate the total marks
def calculate_total(row):
    marks = [row["Principles of AI"], row["Software Construction"], row["Computer Networks"], row["Object Oriented Programming Using Java"], row["Mathematics"]]
    valid_marks = [mark for mark in marks if mark is not None]
    return sum(valid_marks)

def add_marks():
    if st.session_state.new_roll_number and st.session_state.new_name:
        new_row = pd.DataFrame({
            "Roll Number": [st.session_state.new_roll_number],
            "Name": [st.session_state.new_name],
            "Principles of AI": [st.session_state.new_pai_marks if st.session_state.new_pai_marks is not None else None],
            "Software Construction": [st.session_state.new_sc_marks if st.session_state.new_sc_marks is not None else None],
            "Computer Networks": [st.session_state.new_cn_marks if st.session_state.new_cn_marks is not None else None],
            "Object Oriented Programming Using Java": [st.session_state.new_oopj_marks if st.session_state.new_oopj_marks is not None else None],
            "Mathematics": [st.session_state.new_math_marks if st.session_state.new_math_marks is not None else None],
        })
        # Check if the roll number already exists
        if st.session_state.new_roll_number in st.session_state.master_df["Roll Number"].values:
            st.error(f"Roll Number '{st.session_state.new_roll_number}' already exists.")
        else:
            st.session_state.master_df = pd.concat([st.session_state.master_df, new_row], ignore_index=True)
            st.success(f"Marks for '{st.session_state.new_name}' added successfully!")
            # Clear the form inputs after successful submission
            st.session_state.new_roll_number = ""
            st.session_state.new_name = ""
            st.session_state.new_pai_marks = None
            st.session_state.new_sc_marks = None
            st.session_state.new_cn_marks = None
            st.session_state.new_oopj_marks = None
            st.session_state.new_math_marks = None
    else:
        st.error("Roll Number and Name are required.")

def teacher_login_callback():
    if st.session_state.teacher_username == "teacher" and st.session_state.teacher_password == "password":
        st.session_state.logged_in = True
        st.session_state.user_role = "teacher"
        st.success("Teacher login successful!")
    else:
        st.error("Invalid username or password.")

def student_login_callback():
    if st.session_state.student_roll in st.session_state.master_df["Roll Number"].astype(str).values:
        st.session_state.logged_in = True
        st.session_state.user_role = "student"
        st.session_state.student_roll_number = st.session_state.student_roll
        st.success("Student login successful!")
    else:
        st.error("Invalid Roll Number.")

def logout_callback():
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.student_roll_number = None
    st.success("Logged out successfully!")

def login():
    st.title("Student Mark Management System")
    role = st.selectbox("Select your role:", ["Teacher", "Student"], key="login_role")

    if role == "Teacher":
        username = st.text_input("Username:", key="teacher_username")
        password = st.text_input("Password:", type="password", key="teacher_password")
        login_button = st.button("Teacher Login", on_click=teacher_login_callback)

    elif role == "Student":
        roll_number = st.text_input("Enter your Roll Number:", key="student_roll")
        login_button = st.button("View Marks", on_click=student_login_callback)

def teacher_dashboard():
    st.subheader("Teacher Dashboard")
    st.button("Logout", on_click=logout_callback)
    st.subheader("Master Mark Table")

    if not st.session_state.master_df.empty:
        st.session_state.master_df["Total"] = st.session_state.master_df.apply(calculate_total, axis=1)

        # Define the display column names
        display_columns = {
            "Roll Number": "Roll No.",
            "Name": "Student Name",
            "Principles of AI": "POAI",
            "Software Construction": "SC",
            "Computer Networks": "Comp. Networks",
            "Object Oriented Programming Using Java": "OOPJ",
            "Mathematics": "Maths",
            "Total": "Total Marks"
        }

        # Create a new DataFrame with renamed columns for display
        display_df = st.session_state.master_df.rename(columns=display_columns)
        st.dataframe(display_df)

        st.subheader("Data Analysis")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Subject-wise Average Marks")
            subject_columns = ["Principles of AI", "Software Construction", "Computer Networks", "Object Oriented Programming Using Java", "Mathematics"]
            avg_marks = st.session_state.master_df[subject_columns].mean().sort_values(ascending=False)
            st.bar_chart(avg_marks)

        with col2:
            st.subheader("Distribution of Total Marks")
            fig = px.histogram(st.session_state.master_df, x="Total", nbins=10, title="Total Marks Distribution")
            st.plotly_chart(fig)

        st.subheader("Download Master Data")
        buffer = BytesIO()
        st.session_state.master_df.to_excel(buffer, index=False, sheet_name="Master Marks")
        st.download_button(
            label="Download as Excel",
            data=buffer,
            file_name="master_marks.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    else:
        st.info("No student marks data available yet.")

    st.subheader("Teacher Dashboard - Add New Student Marks")
    with st.form("new_student_marks"):
        st.text_input("Roll Number:", key="new_roll_number")
        st.text_input("Name:", key="new_name")
        st.number_input("POAI Marks:", min_value=0, max_value=100, key="new_pai_marks")
        st.number_input("SC Marks:", min_value=0, max_value=100, key="new_sc_marks")
        st.number_input("Comp. Networks Marks:", min_value=0, max_value=100, key="new_cn_marks")
        st.number_input("OOPJ Marks:", min_value=0, max_value=100, key="new_oopj_marks")
        st.number_input("Maths Marks:", min_value=0, max_value=100, key="new_math_marks")
        st.form_submit_button("Add Marks", on_click=add_marks)

def student_dashboard():
    st.subheader("Student Dashboard")
    st.button("Logout", on_click=logout_callback)
    if "student_roll_number" in st.session_state:
        roll_number = st.session_state.student_roll_number
        st.write(f"Welcome, Student with Roll Number: {roll_number}!")
        if roll_number in st.session_state.master_df["Roll Number"].astype(str).values:
            student_data = st.session_state.master_df[st.session_state.master_df["Roll Number"].astype(str) == roll_number].iloc[0]
            marks_to_display = {k: v for k, v in student_data.items() if k not in ["Roll Number", "Name"]}
            total_marks = calculate_total(student_data)

            st.subheader("Your Marks:")
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            with col1:
                st.metric(label="POAI", value=student_data["Principles of AI"] if pd.notna(student_data["Principles of AI"]) else "N/A")
            with col2:
                st.metric(label="SC", value=student_data["Software Construction"] if pd.notna(student_data["Software Construction"]) else "N/A")
            with col3:
                st.metric(label="Comp. Networks", value=student_data["Computer Networks"] if pd.notna(student_data["Computer Networks"]) else "N/A")
            with col4:
                st.metric(label="OOPJ", value=student_data["Object Oriented Programming Using Java"] if pd.notna(student_data["Object Oriented Programming Using Java"]) else "N/A")
            with col5:
                st.metric(label="Maths", value=student_data["Mathematics"] if pd.notna(student_data["Mathematics"]) else "N/A")
            with col6:
                st.metric(label="Total Marks", value=total_marks if total_marks is not None else "N/A")

            st.subheader("Your Performance")
            subject_marks = {
                "POAI": student_data.get("Principles of AI", None),
                "SC": student_data.get("Software Construction", None),
                "Comp. Networks": student_data.get("Computer Networks", None),
                "OOPJ": student_data.get("Object Oriented Programming Using Java", None),
                "Maths": student_data.get("Mathematics", None),
            }
            valid_subject_marks = {k: v for k, v in subject_marks.items() if v is not None}

            if valid_subject_marks:
                fig = px.bar(x=list(valid_subject_marks.keys()), y=list(valid_subject_marks.values()),
                             title="Your Subject-wise Marks", labels={'x': 'Subject', 'y': 'Marks'})
                st.plotly_chart(fig)

            # Create a PDF object
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=10)  # Slightly smaller font to fit more columns

            # Title
            pdf.cell(200, 10, txt=f"Marks for Roll Number: {roll_number}", ln=1, align="C")

            # Table headers
            pdf.cell(50, 10, txt="Subject", border=1)
            pdf.cell(30, 10, txt="Marks", border=1, ln=1)

            # Table rows
            pdf.cell(50, 10, txt="POAI", border=1)
            pdf.cell(30, 10, txt=str(student_data.get("Principles of AI", "N/A")), border=1, ln=1)
            pdf.cell(50, 10, txt="SC", border=1)
            pdf.cell(30, 10, txt=str(student_data.get("Software Construction", "N/A")), border=1, ln=1)
            pdf.cell(50, 10, txt="Comp. Networks", border=1)
            pdf.cell(30, 10, txt=str(student_data.get("Computer Networks", "N/A")), border=1, ln=1)
            pdf.cell(50, 10, txt="OOPJ", border=1)
            pdf.cell(30, 10, txt=str(student_data.get("Object Oriented Programming Using Java", "N/A")), border=1, ln=1)
            pdf.cell(50, 10, txt="Maths", border=1)
            pdf.cell(30, 10, txt=str(student_data.get("Mathematics", "N/A")), border=1, ln=1)
            pdf.cell(50, 10, txt="Total Marks", border=1)
            pdf.cell(30, 10, txt=str(total_marks if total_marks is not None else "N/A"), border=1, ln=1)

            # Generate PDF bytes
            pdf_bytes = bytes(pdf.output(dest="S"))

            st.download_button(
                label="Download Marks (PDF)",
                data=pdf_bytes,
                file_name=f"marks_roll_{roll_number}.pdf",
                mime="application/pdf",
            )

        else:
            st.error("Student data not found.")
    else:
        st.info("Please log in as a student to view your marks.")

# Main App Flow
if not st.session_state.logged_in:
    login()
else:
    if st.session_state.user_role == "teacher":
        teacher_dashboard()
    elif st.session_state.user_role == "student":
        student_dashboard()