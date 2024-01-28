# Import necessary libraries
from ask_vector_and_supplment_with_ai import answer_question
import streamlit as st
from st_click_detector import click_detector

# Title of the Streamlit app
st.title("Ask a Question")

# Using st.form to create a form
with st.form(key='my_form'):
    # Create a text input for the user to enter their question
    question = st.text_input("Please enter your question:")

    # Create a submit button within the form
    submit_button = st.form_submit_button(label='Submit')

# Placeholder for the "Thinking..." message
thinking_placeholder = st.empty()

if submit_button:
    # Show "Thinking..." while waiting for the answer
    thinking_placeholder.text("Thinking...")

    # Fetch the answer and vector results
    answer, vector_results = answer_question(question)

    # Remove the "Thinking..." text
    thinking_placeholder.empty()

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
