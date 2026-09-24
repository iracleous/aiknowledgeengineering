# ChatPromptTemplate: reusable, parameterized message templates

from dotenv import load_dotenv
 
from langchain_core.prompts import ChatPromptTemplate

import os
from langchain_openai import AzureChatOpenAI

load_dotenv()

llm = AzureChatOpenAI(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
)


# Format 1: from_template (simple text, no roles)
template = ChatPromptTemplate.from_template(
    "You are an expert in {domain}. Answer: {question}"
)
messages = template.invoke(
    {"domain": "biology", "question": "How many bones in a human?"}
)


# Format 2: from_messages (most common, structured roles)
template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an expert in {domain}."),
        ("human", "{question}"),
    ]
)
messages = template.invoke({"domain": "astronomy", "question": "How big is the Sun?"})

# Format 3: Multiple system + human turns
template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a {role} expert."),
        ("human", "Question 1: {question1}"),
        ("human", "Question 2: {question2}"),
    ]
)
messages = template.invoke(
    {
        "role": "history",
        "question1": "When was Ancient Rome founded?",
        "question2": "Who was Julius Caesar?",
    }
)

# for all templates above that
print("Messages:", messages)
response = llm.invoke(messages)
print("Response:", response.content)


# Format 4: Reusable template (same template, different values)
expert_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an expert in {domain}."),
        ("human", "{question}"),
    ]
)

domains_and_questions = [
    ("chemistry", "What is H2O?"),
    ("physics", "What is gravity?"),
    ("history", "When was the Parthenon built?"),
]

for domain, question in domains_and_questions:
    messages = expert_template.invoke({"domain": domain, "question": question})
    response = llm.invoke(messages)
    print(f"[{domain}]", response.content)
