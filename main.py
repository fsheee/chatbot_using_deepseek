import streamlit as st
from langchain_groq import ChatGroq
#from langchain.output_parsers import StroutputParser #AI response
from langchain_core.output_parsers import StrOutputParser

from langchain.prompts import (
        SystemMessagePromptTemplate,
        HumanMessagePromptTemplate,
        AIMessagePromptTemplate,
        ChatPromptTemplate
)# chat messages

groq_api_key="paste your api key here"

#display title and subtitle
st.title("🤖 💬 AI Chatbot")
st.subheader("Hi I'm your AI Chatbot, how can I help you?💭 ")

#sidebar configuration for user settings
with st.sidebar:
    st.header("🛠️ ChatBot configuration") #header for sidebar
    seleted_model=st.selectbox("Choose Model",["deepseek-r1-distill-llama-70b"]) #dropdown for model
    st.markdown("### ChatBot Capabilities")# section header for capablities
    capabilities=[
        "💬 General conversation",
        "🐍 Python Expert",
        "🐞 Debugging Assistant",
        "📄 Code Documentation",
        "🏗️ Solution design",
        "🔎 Information Retrieval"
    ]    #list of capablitites
    
    st.multiselect("Select Capabilities",capabilities,default=capabilities)#multiselect for capabilities
    with st.expander("### ✨ Quick Tips"):
         st.markdown("""
                     - **Tip 1**: Use the chatbot for general conversation.
                     - **Tip 2**: Leverage the Python expertise for coding and debugging.
                     - **Tip 3**: Utilize information retrieval for quick access to data and facts.
                     """)  #tips for using the chatbot
    
    #initilize the chat engine with selected  model
    llm=ChatGroq(api_key=groq_api_key, model_name=seleted_model,temperature=0.3)
     
    #function to build the system prompt based on selected capabilities
    def build_system_prompt(selected_capabilities):
        capabilities_text ="," .join(selected_capabilities) #join capabilities into a string
        return f"You are a versatile AI chatbot with the following capabilities:{capabilities_text}.Engage in general conversation"
    
    #create system prompt using the seleted capabilities
    system_prompt=SystemMessagePromptTemplate.from_template(
        build_system_prompt(capabilities)
    )
    
    #initilize session state for message log
    if "message_log" not in st.session_state:
        st.session_state.message_log=[] #initilize message log if not pressent
    
    # container for displaying chat messages logs
    chat_container=st.container()
    #display chat messages from the message log  
    with chat_container:
        for message in st.session_state.message_log:
            with st.chat_message(message["role"]):#display each msg with its role
               if "<think>" in message["content"] and "</think>" in message["content"]:
                   start_idx=message["content"].find("<think>") + len("<think>")
                   end_idx=message["content"].find("</think>")
                   think_content=message["content"][start_idx:end_idx].strip() #extract thinking content
                   actual_response=message["content"][end_idx + len("</think>"):].strip() #extract actual response
                   with st.expander("🤖💭 AI Thought Process"):#expandable section for thought process
                    st.markdown(think_content)
                   st.markdown(actual_response) #display actual content
               else:
                   st.markdown(message["content"]) #display content    

# input field for user queries
user_query=st.chat_input("Type your question or topic here....")                   

# function to generate AI response
def generate_ai_response(prompt_chain):
    #llm_engine = llm  # Define llm_engine
    processing_pipeline = prompt_chain | llm | StrOutputParser()  # create processing pipeline
    return processing_pipeline.invoke({})  # Invoke processing pipeline to get response

#function to bulid a prompt chain for the chat
def build_prompt_chain():
    prompt_sequence=[system_prompt] # start with the system prompt
    for message in st.session_state.message_log:
        if message["role"]=="user": #add user message to the prompt chain
            prompt_sequence.append(HumanMessagePromptTemplate.from_template(message["content"])) #add write msg
        elif message["role"]=="AI":#add AI message to the prompt chain
            prompt_sequence.append(AIMessagePromptTemplate.from_template(message["content"])) #add AI msg
    return ChatPromptTemplate.from_messages(prompt_sequence) #return complate prompt chain

#process user query if present
if user_query:
    st.session_state.message_log.append({"role":"user","content":user_query}) #add user query to the message log
    with st.spinner("⏳ Processing..."): #show spinnet while processing
        prompt_chain=build_prompt_chain() #build prompt chain 
        ai_response=generate_ai_response(prompt_chain) #generate AI response
    st.session_state.message_log.append({"role":"AI","content":ai_response})#add AI response to the message log
    st.rerun() #return the app to update the display

