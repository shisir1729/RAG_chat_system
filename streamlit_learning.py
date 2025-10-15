import streamlit as st
import requests

url = "http://127.0.0.1/8000"
upload_url = "http://localhost:8000/upload"
query_url = "http://localhost:8000/query"

st.title("The RAG System")
if 'messages' not in st.session_state:
    st.session_state.messages = []


with st.sidebar:
    st.header("upload Document")

    uploaded_file = st.file_uploader("choose a file",type=['pdf'])
    
    if uploaded_file is not None:
            if st.button("Upload File", type="primary"):
                with st.spinner("Uploading..."):
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                        response = requests.post(upload_url, files=files)
                        
                        if response.status_code == 200:
                            st.success("File uploaded successfully!")
                            st.session_state.upload_success = True
                        else:
                            st.error(f"Upload failed: {response.text}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}") 


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about your documents..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Query is passed as path parameter
                response = requests.post(f"{query_url}/{prompt}")
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Extract response based on your API structure
                    if isinstance(result, dict):
                        if 'answer' in result:
                            response_text = result['answer']
                        elif 'response' in result:
                            response_text = result['response']
                        else:
                            response_text = str(result)
                    else:
                        response_text = str(result)
                    
                    st.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                else:
                    error_msg = f"❌ Query failed: {response.text}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})