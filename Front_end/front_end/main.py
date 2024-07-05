import streamlit as st
import requests
import os

def main():
    st.markdown("""
    <div style="text-align: center;">
    <h1>FJ Brainstorm Blitz</h1>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center;">
    Explore your future learning!
    </div>
    """, unsafe_allow_html=True)

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    base_url = os.getenv('API_URL', 'http://127.0.0.1:8000')

    if not st.session_state['logged_in']:
        login_or_register(base_url)
    else:
        generate_mcqs_section(base_url)
        if 'mcqs' in st.session_state:
            generate_result_section(base_url)  # Display the "Generate result" button only if MCQs have been generated
        logout_button()

def login_or_register(base_url):
    menu = ["Login", "Register"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":
        login_page(base_url)
    elif choice == "Register":
        register_page(base_url)

def login_page(base_url):
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if not username or not password:
            st.error("Username and password are required.")
            return
        try:
            response = requests.post(f"{base_url}/login/?username={username}&password={password}")
            response.raise_for_status()
            
            st.session_state['logged_in'] = True
            st.session_state['token'] = response.json()['token']
            st.success("Login successful!")
            st.rerun()
        except requests.exceptions.HTTPError as err:
            st.error(f"Login Failed: {err}")
        except requests.exceptions.RequestException as err:
            st.error(f"An error occurred: {err}")

def register_page(base_url):
    st.subheader("Create Account")
    new_username = st.text_input("Username")
    new_password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    email = st.text_input("Email Address")
    
    if st.button("Register"):
        if not new_username or not new_password or not confirm_password or not email:
            st.error("All fields are required.")
            return
        if new_password != confirm_password:
            st.error("Password confirmation doesn't match password.")
            return
        try:
            response = requests.post(f"{base_url}/register/?username={new_username}&password={new_password}&password_confirm={confirm_password}&email={email}")
            response.raise_for_status()
            st.success("Registration Successful!")
            st.write("You can now login with your new account.")
            st.info("A confirmation email has been sent to your email address.")
        except requests.exceptions.HTTPError as err:
            st.error(f"Registration Failed: {err}")
        except requests.exceptions.RequestException as err:
            st.error(f"An error occurred: {err}")


def generate_mcqs_section(base_url):
    st.markdown("""
    <div style="text-align: center;">
    FJ Brainstorm Blitz is a dynamic application revolutionizing the creation of multiple-choice questions (MCQs), tailored to users' expertise and interests. By entering their area of expertise or preferred topic, users prompt the app to generate a customized set of MCQs. FJ Brainstorm Blitz not only facilitates quiz creation but also fosters learning through personalized suggestions based on user-generated questions and answers. With its user-friendly interface and AI-powered features, FJ Brainstorm Blitz aims to elevate learning experiences and promote knowledge acquisition across various disciplines and educational contexts.
    </div>
    """, unsafe_allow_html=True)

    if 'mcqs' not in st.session_state:
        topic_input = st.text_input("Enter the topic for MCQs")
        if st.button("Generate MCQs"):
            try:
                token = st.session_state['token']
                headers = {"Authorization": f"Bearer {token}"}
                with st.spinner('Generating MCQs...'):
                    response = requests.post(f"{base_url}/generate_mcqs/?topic_input={topic_input}", headers=headers)
                    response.raise_for_status()
                    mcqs = response.json()['mcqs']
                    st.session_state.mcqs = mcqs
                    if mcqs:
                        st.success("MCQs generated successfully!")
                        st.session_state.collected_answers = [None] * min(20, len(mcqs))
                        show_mcqs_and_answers(mcqs)
                    else:
                        st.error("Failed to generate MCQs.")
            except KeyError:
                st.error("Please login first to generate MCQs.")
            except requests.exceptions.HTTPError as err:
                st.error(f"Failed to generate MCQs: {err}")
            except requests.exceptions.RequestException as err:
                st.error(f"An error occurred: {err}")
    else:
        show_mcqs_and_answers(st.session_state.mcqs)

def show_mcqs_and_answers(mcqs):
    st.write(mcqs)
    st.subheader("Enter Answers for the MCQs:")
    columns = st.columns(4)
    for i in range(min(20, len(mcqs))):
        with columns[i % 4]:
            options = [str(option) for option in ['A', 'B', 'C', 'D']]  # Ensure options are strings
            st.session_state.collected_answers[i] = st.radio(
                f"Answer for MCQ {i+1}:", 
                options=options, 
                index=options.index(st.session_state.collected_answers[i]) if st.session_state.collected_answers[i] is not None else 0
            )
    
def generate_result_section(base_url):
    if st.button("Generate result"):
        try:
            # Check if user is logged in
            if not st.session_state.get('logged_in'):
                st.error("Please login first to generate results.")
                return

            # Ensure token is available in session state
            token = st.session_state.get('token')
            if not token:
                st.error("Authentication token not found.")
                return

            headers = {"Authorization": f"Bearer {token}"}
            collected_answers = st.session_state.collected_answers
            result = st.session_state.mcqs
            if not result or not collected_answers:
                st.error("No MCQs or collected answers found.")
                return
            
            with st.spinner('Generating Result...'):
                # Send collected answers to the server for grading
                response = requests.post(f"{base_url}/generate_result/?result={result}&collected_answers={collected_answers}", headers=headers)
                response.raise_for_status()
                
                # Display the result
                result = response.json().get("result")
                # Display the result
                results = response.json()
                st.write(f"**Answer Keys:**\n {results.get('result1')}")
                st.write(f"**Matching Answers:**\n {results.get('result2')}")
                st.write(f"**Summarized Result:**\n {results.get('result3')}")
                st.write(f"**Learning Suggestions:**\n {results.get('result4')}")
                
        except requests.exceptions.HTTPError as err:
            st.error(f"Failed to generate result: {err}")
        except requests.exceptions.RequestException as err:
            st.error(f"An error occurred: {err}")


def logout_button():
    if st.button("Logout"):
        st.session_state['logged_in'] = False
        st.session_state.pop('token', None)
        st.session_state.pop('mcqs', None)
        st.session_state.pop('collected_answers', None)
        st.rerun()

if __name__ == "__main__":
    main()