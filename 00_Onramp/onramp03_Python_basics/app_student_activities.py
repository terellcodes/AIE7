import streamlit as st
import pandas as pd
import openai
import datetime
import re
import os
from dotenv import load_dotenv

load_dotenv()

# Set your OpenAI API key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

# Setup OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Streamlit UI
st.title("🧠 LLM Python Challenge App")
st.write("👋 Welcome! This interactive app includes several Python tasks to test your data skills.")
st.warning("⚠️ Some tasks are left unfinished on purpose — **fill them in to complete the app**!")

# 🏗️ Activity 1: Create a pandas DataFrame
st.header("🏗️ Activity 1: Create a pandas DataFrame")
st.markdown("Your DataFrame should have the columns: `name` (str), `score` (int), `date` (yyyy-mm-dd).")
st.info("✍️ Task: Replace the placeholder with your own DataFrame code.")

# Placeholder: students will fill this in
df = None  # ← replace this with your DataFrame

# 🏗️ Activity 2: Preview the DataFrame
st.header("🏗️ Activity 2: Preview the DataFrame")
st.markdown("Use Streamlit to display your DataFrame.")

if df is not None:
    st.dataframe(df)
else:
    st.write("⚠️ DataFrame not defined yet — complete Activity 1!")

# 🏗️ Activity 3: Filter data
st.header("🏗️ Activity 3: Filter the DataFrame")
st.markdown("Filter rows where score > 85. Display the filtered DataFrame.")
st.info("✍️ Task: Add filtering logic here.")

# 🏗️ Activity 4: Use regex to extract names with A or B
st.header("🏗️ Activity 4: Use regex")
st.markdown("Extract names starting with 'A' or 'B' using regex.")
st.info("✍️ Task: Use the `re` library here.")

# 🏗️ Activity 5: Calculate average score by date
st.header("🏗️ Activity 5: Average Score by Date")
st.info("✍️ Task: Group by date and calculate the average score.")

# 🏗️ Activity 6: Chat with OpenAI
st.header("🏗️ Activity 6: Chat with OpenAI")
st.markdown("Ask a question - what is the average score by date? What score has a student?, and the OpenAI model will respond!")

user_prompt = st.text_area("Enter your prompt:", "")
if st.button("Send to OpenAI") and user_prompt:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_prompt}]
        )
        reply = response.choices[0].message.content
        st.success("Response:")
        st.write(reply)
    except Exception as e:
        st.error(f"Error: {e}")
