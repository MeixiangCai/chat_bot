#项目目标是创作一个帮助学习的对话机器人
import streamlit as st
from langchain.chains.conversation import ConversationChain #本项目使用旧版langchain
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate,MessagesPlaceholder
#进行前端网页设计
st.title("经济学人伴读助手")
with st.sidebar:
    subject=st.selectbox(
        "选择领域",
        options=["通用","政治","经济","科技","军事","文化"],
    )
    style=st.selectbox(
        "讲解风格",
        options=["简洁","详细"],
    )
#st.chat_message("assistant").write("你好，我是你的学习助手！请问有什么可以帮你的吗？")
#user_input=st.chat_input("你的问题/学习需求")
#st.chat_message("human").write(user_input)

#一个聊天输入框，提示用户输入问题
user_input=st.chat_input("你遇到的表达/困惑")
#判断当前是否有会话，如果没有，则初始化消息列表和记忆
if "messages" not in st.session_state:
    st.session_state["messages"]=[
        {"role":"assistant", "content":"你好，我是你的学习助手！"}
    ]
    st.session_state["memory"]=ConversationBufferMemory(
        memory_key="chat_history",return_messages=True
    )
#遍历messages列表中的每条消息并且显示在聊天界面上
for message in st.session_state["messages"]:
    st.chat_message(message["role"]).write(message["content"])
#定义提示词模板的函数
def get_prompt_template(subject,style):
    style_dict={
        "简洁": "仅提供直接答案和最少的必要解释。不要添加额外细节、发散讨论或无关信息。保持回答清晰、简洁，目标是为用户快速提供解决方案。",
        "详细": "第一，针对用户提问给出直接答案和清晰的解释；第二，基于此提供必要的相关知识点的信息，以补充背景或加深理解。",
    }
    system_template="你是{subject}领域的中英双语专家，你熟悉经济学人，用户输入英文表达时，你用中文向用户解释其在经济学人中的含义，用户输入中文提问时，你依然用中文进行解答。\n你需要遵循以下讲解风格：{style}。\n你应当礼貌拒绝与该学科无关的问题。"
    #正式创建一个聊天提示词模板
    prompt_template=ChatPromptTemplate(
        [
            ("system",system_template),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human","{input}")
        ],
        partial_variables={"subject":subject,"style":style_dict[style]},
    )
    return prompt_template
#定义AI回复的函数
def generate_response(user_input,subject,style,memory):
    client=ChatOpenAI(
        api_key=st.secrets["OPENAI_API_KEY"],
        model="deepseek-chat",
        base_url="https://api.deepseek.com",
        temperature=1.3,
    )
    prompt=get_prompt_template(subject,style)
    chain=ConversationChain(
        llm=client,
        memory=memory,
        prompt=prompt,
    )
    response=chain.invoke({"input":user_input})
    return response["response"]
#如果已有用户输入
if user_input:
    st.chat_message("human").write(user_input)
    st.session_state["messages"].append({"role":"human","content":user_input})
    #显示AI思考的过程
    with st.spinner("AI正在思考中，请稍等..."):
        response=generate_response(
            user_input,subject,style,st.session_state["memory"]
        )
    #将AI生成的回复显示在聊天界面
    st.chat_message("assistant").write(response)
    #再将AI的回复添加到会话状态的消息列表中
    st.session_state["messages"].append({"role":"assistant","content":response})
