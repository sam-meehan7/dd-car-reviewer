# Import necessary libraries
from ask_vector_and_supplment_with_ai import answer_question
import streamlit as st
from st_click_detector import click_detector
import random

# Define an array of fun facts
fun_facts = [
    "DoneDeal has over 70,000 cars for sale!",
    "DoneDeal has over 15,000 electric and hybrid cars for sale!"
]

# Title of the Streamlit app
st.title("DoneDeal Car Reviews")

# Using st.form to create a form
with st.form(key='my_form'):
    # Create a text input for the user to enter their question
    question = st.text_input("Please tell us what you are looking for:")

    # Create a submit button within the form
    submit_button = st.form_submit_button(label='Submit')


fun_fact_placeholder = st.empty()

if submit_button:
    # Select a random fun fact
    fun_fact = random.choice(fun_facts)

    # Display the fun fact and loading message
    with fun_fact_placeholder.container():
        st.markdown(f"💡 *While you wait, did you know:*\n\n{fun_fact}")
        with st.spinner('Fetching your results...'):
            # Fetch the answer and vector results
            answer, vector_results = answer_question(question)

    # Clear the status (fun fact and loading message)
    fun_fact_placeholder.empty()

    # Display the answer
    st.write(answer)

    # Display source links in a grid format
    st.subheader("Source Links:")

    # Initialize the HTML content
    html_content = "<div style='display: flex; flex-wrap: wrap;'>"

    for result in vector_results:
        # Extract necessary data from the result's metadata
        title = result.metadata["title"]
        url = result.metadata["url"]
        start_time = result.metadata["start"]
        thumbnail = result.metadata["thumbnail"]

        # Construct the URL with start time appended
        clickable_url = f"{url}&t={int(start_time)}s"

        # Append each grid item to the HTML content
        html_content += f"""
        <div style='flex: 33%; padding: 5px; text-align: center;'>
            <a href='{clickable_url}' target='_blank'>
                <img src='{thumbnail}' width='100'>
                <p>{title}</p>
            </a>
        </div>
        """

    # Close the div
    html_content += "</div>"

    click_detector(html_content)
