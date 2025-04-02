import streamlit as st
import pandas as pd
from langchain.document_loaders import PyPDFLoader
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import OpenAI
from langchain.chat_models import init_chat_model
from pydantic import BaseModel
from typing import Annotated,List
import random

st.header("Generate Questions from Book/PDF")

os.environ["OPENAI_API_KEY"]="*********" # Put your OpenAI API key here


llm = init_chat_model("gpt-4o-mini", model_provider="openai",temperature=0)

st.sidebar.header("Upload Your Book in pdf format")
files = st.sidebar.file_uploader('Upload multiple files',accept_multiple_files=True)

if files:
    file_names = [file.name for file in files]

    selected_file = st.sidebar.selectbox("Select the Chapters", file_names)
    
    if selected_file:
        file_dict = {file.name: file for file in files}
        file_obj = file_dict[selected_file]

        temp_path = f"temp_{selected_file}"
        with open(temp_path, "wb") as f:
            f.write(file_obj.read())

        loader = PyPDFLoader(temp_path)
        docs = loader.load()
        full_text = " ".join([page.page_content for page in docs])
        


with st.form(key='my_form'):
    question_type = st.selectbox(
        "Select Type of Questions:", 
        ["Short Descriptive", "Long Descriptive", "Multiple Choice", "True/False", "Word-Puzzle"]
    )
    num_questions = st.number_input("Select a number", min_value=0, max_value=25, value=10, step=1)

    include_answer = st.toggle("Include Answer")

    submit_button = st.form_submit_button(label="Submit")


if submit_button:
    if question_type=='Short Descriptive':
        class Review(BaseModel):
            Serial_No : Annotated[List[int],'Serial number of the question']
            Questions: Annotated[List[str],'Question statement']
            Answer:Annotated[List[str],'Descriptive answer']
        structured_model=llm.with_structured_output(Review)
        result=structured_model.invoke(f'Frame exactly {num_questions} question/questions with solution out of the text. Questions are short descriptive e.g. for 2 marks. Note that the question should not refer to the text as students does not have access to the text while answering the questions : \n {full_text}')
    
        df=pd.DataFrame({'Serial_no':result.Serial_No, 'Question':result.Questions, 'Answer':result.Answer})
        if include_answer==True:
            st.dataframe(df,
                         hide_index=True)

        else:
            st.dataframe(df[['Serial_no','Question']],
                         hide_index=True)
        
    elif question_type=='Long Descriptive':
        class Review(BaseModel):
            Serial_No : Annotated[List[int],'Serial number of the question']
            Questions: Annotated[List[str],'Question statement']
            Answer:Annotated[List[str],'Descriptive answer']
        structured_model=llm.with_structured_output(Review)
        result=structured_model.invoke(f'Frame exactly {num_questions} question/questions with solution out of the text. Questions are long descriptive e.g. for 5 to 10 marks. Note that the question should not refer to the text as students does not have access to the text while answering the questions : \n {full_text}')
    
        df=pd.DataFrame({'Serial_no':result.Serial_No, 'Question':result.Questions, 'Answer':result.Answer})
        if include_answer==True:
            st.dataframe(df,
                         hide_index=True)
        else:
            st.dataframe(df[['Serial_no','Question']],
                         hide_index=True)
    elif question_type=='Multiple Choice':
        class Review(BaseModel):
            Serial_No:Annotated[List[int],'Serial number of the question']
            Question: Annotated[List[str],'Question statement']
            Option_A: Annotated[List[str],'List of option A']
            Option_B: Annotated[List[str],'List of option B']
            Option_C: Annotated[List[str],'List of option C']
            Option_D: Annotated[List[str],'List of option D']
            Answer:   Annotated[List[str],"The correct option out of 'A','B','C' and 'D'"]
            Explanation: Annotated[List[str],'Explanation of the correct answer']
        structured_model=llm.with_structured_output(Review)
        result=structured_model.invoke(f'Frame {num_questions} MCQ questions with their options and solution out of the text. Append all 1st option of all the questions in Option_A.Append all 2nd option of all the questions in Option_B. Append all 3rd option of all the questions in Option_C. Append all 4th option of all the questions in Option_D. Questions are Multiple choice correct type. Note that the question should not refer to the text as students does not have access to the text while answering the questions : \n {full_text}')
    
        df=pd.DataFrame({'Serial_no':result.Serial_No, 'Question':result.Question,'Option A':result.Option_A,'Option B':result.Option_B,'Option C':result.Option_C,'Option D':result.Option_D,'Answer':result.Answer,'Explanation':result.Explanation})
        if include_answer==True:
            st.dataframe(df,
                         hide_index=True)
        else:
            st.dataframe(df[['Serial_no','Question','Option A','Option B','Option C','Option D']],
                         hide_index=True)
                    
    elif question_type=='True/False':
        class Review(BaseModel):
            Serial_No : Annotated[List[int],'Serial number of the question']
            Question: Annotated[List[str],'Question statement']
            Answer:Annotated[List[str],'Either True or False']
        structured_model=llm.with_structured_output(Review)
        result=structured_model.invoke(f'Frame exactly {num_questions} question/questions out of the text whose answer is either True or False. Questions are short statements which can either be true or false. Note that the question should not refer to the text as students does not have access to the text while answering the questions : \n {full_text}')
    
        df=pd.DataFrame({'Serial_no':result.Serial_No, 'Question':result.Question, 'Answer':result.Answer})
        if include_answer==True:
            st.dataframe(df,
                         hide_index=True)
        else:
            st.dataframe(df[['Serial_no','Question']],
                         hide_index=True)
    
    elif question_type=='Word-Puzzle':
        class Review(BaseModel):
            Serial_No : Annotated[List[int],'Serial number of the question']
            Question: Annotated[List[str],'Descriptive question statement']
            Answer:Annotated[List[str],'Answer must be of exactly one word']
            
        structured_model=llm.with_structured_output(Review)
        result=structured_model.invoke(f'Frame {num_questions} questions out of the text. The answer should be of exactly one word and should not have any special character. Note that the question should not refer to the text as students does not have access to the text while answering the questions : \n {full_text}')
        def fun(s):
            a,b=random.sample(range(0, len(s)), 2)
            list1=[]
            for i in range(len(s)):
                if i==a or i==b:
                    list1.append(s[i])
                else:
                    list1.append('_')
            return " ".join(list1)
            
        df=pd.DataFrame({'Serial_no':result.Serial_No, 'Question':result.Question, 'Answer':result.Answer})
        df['Cue']=df['Answer'].apply(fun)
        if include_answer==True:
            st.dataframe(df[['Serial_no','Question','Cue','Answer']],
                         hide_index=True)
        else:
            st.dataframe(df[['Serial_no','Question','Clue']],
                         hide_index=True)
                        