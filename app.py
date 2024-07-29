import streamlit as st
import google.generativeai as genai
import os
import pandas as pd

# Set up the API key
#os.environ['GOOGLE_API_KEY'] = 'your_api_key_here'
#os.environ['GOOGLE_API_KEY'] = 'AIzaSyAGho3ZFXiX_gguR5GhhtztKTgr0iHLqlg'
genai.configure(api_key='AIzaSyAGho3ZFXiX_gguR5GhhtztKTgr0iHLqlg')

@st.cache_resource
def load_gemini_model():
    return genai.GenerativeModel('gemini-pro')
model = load_gemini_model()

# Load the dataset
@st.cache_data
def load_data():
    return pd.read_csv('data.csv')  # Replace with your actual file path

def generate_content(prompt):
    response = model.generate_content(prompt)
    return response.text

def main():
    st.set_page_config(layout="wide")
    st.title("Civic Response Assistant Dashboard")

    df = load_data()

    st.header("Disaster Information and Summary")

    # Allow user to search for a disaster
    search_term = st.text_input("Search for a disaster (e.g., country, year, disaster type):")
    
    if search_term:
        # Filter the dataframe based on the search term
        filtered_df = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
        
        if not filtered_df.empty:
            st.write(f"Found {len(filtered_df)} matching disasters:")
            selected_disaster = st.selectbox("Select a disaster to view details:", 
                                             filtered_df.index, 
                                             format_func=lambda i: f"{filtered_df.loc[i, 'Year']} - {filtered_df.loc[i, 'Country']} - {filtered_df.loc[i, 'Disaster Type']}")
            
            disaster_data = filtered_df.loc[selected_disaster]
            
            st.subheader("Disaster Details")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Year", disaster_data['Year'])
                st.metric("Country", disaster_data['Country'])
            with col2:
                st.metric("Disaster Type", disaster_data['Disaster Type'])
                st.metric("Disaster Subtype", disaster_data['Disaster Subtype'])
            with col3:
                st.metric("Total Deaths", disaster_data['Total Deaths'])
                st.metric("Total Affected", disaster_data['Total Affected'])

            tabs = st.tabs(["Summary", "Public Information", "Citizen Engagement", "Educational Content"])

            with tabs[0]:
                st.subheader("Disaster Summary")
                prompt = f"Generate a comprehensive paragraph summarizing the following disaster:\n\n"
                for column in disaster_data.index:
                    prompt += f"{column}: {disaster_data[column]}\n"
                summary = generate_content(prompt)
                st.info(summary)

            with tabs[1]:
                st.subheader("Public Information and Updates")
                prompt = f"Based on the following disaster information, generate a public information update for citizens:\n\n"
                for column in disaster_data.index:
                    prompt += f"{column}: {disaster_data[column]}\n"
                prompt += "\nInclude current status, safety measures, and any relevant updates."
                public_info = generate_content(prompt)
                st.warning(public_info)

            with tabs[2]:
                st.subheader("Citizen Engagement")
                col1, col2 = st.columns(2)
                with col1:
                    prompt = f"Create a citizen engagement plan for the following disaster:\n\n"
                    for column in disaster_data.index:
                        prompt += f"{column}: {disaster_data[column]}\n"
                    prompt += "\nInclude ways for citizens to help, report issues, and stay informed."
                    engagement_plan = generate_content(prompt)
                    st.success(engagement_plan)
                
                with col2:
                    st.subheader("Disaster Response Chatbot")
                    user_question = st.text_input("Ask a question about the disaster:")
                    if user_question:
                        chat_prompt = f"Based on the following disaster information:\n\n"
                        for column in disaster_data.index:
                            chat_prompt += f"{column}: {disaster_data[column]}\n"
                        chat_prompt += f"\nAnswer the following question: {user_question}"
                        response = generate_content(chat_prompt)
                        st.write("Chatbot: " + response)

            with tabs[3]:
                st.subheader("Educational Content")
                prompt = f"Develop educational content related to the following disaster type:\n\n"
                prompt += f"Disaster Type: {disaster_data['Disaster Type']}\n"
                prompt += f"Disaster Subtype: {disaster_data['Disaster Subtype']}\n"
                prompt += "\nInclude prevention measures, preparedness tips, and general information about this type of disaster."
                educational_content = generate_content(prompt)
                
                # Split the content into sections
                sections = educational_content.split('\n\n')
                for i, section in enumerate(sections):
                    with st.expander(f"Section {i+1}"):
                        st.write(section)

        else:
            st.write("No matching disasters found.")

if __name__ == "__main__":
    main()
