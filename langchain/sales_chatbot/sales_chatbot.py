import gradio as gr
import sys
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAI


def initialize_sales_bot(vector_store_dir: str="real_estates_sale"):
    db = FAISS.load_local(vector_store_dir,OpenAIEmbeddings(base_url="https://api.xiaoai.plus/v1",api_key="sk-tdqfro61NniG2LZd5394E5F28c51419d8b4dE7Db5a6105C4"),allow_dangerous_deserialization=True)
    llm = ChatOpenAI(model_name="gpt-4", temperature=0,base_url="https://api.xiaoai.plus/v1",api_key="sk-tdqfro61NniG2LZd5394E5F28c51419d8b4dE7Db5a6105C4")
    
    global SALES_BOT    
    SALES_BOT = RetrievalQA.from_chain_type(llm,
                                           retriever=db.as_retriever(search_type="similarity_score_threshold",
                                                                     search_kwargs={"score_threshold": 0.8}))
    # 返回向量数据库的检索结果
    SALES_BOT.return_source_documents = True

    return SALES_BOT

def sales_chat(user_input, history, enable_chat=True):
    print(f"[message]{user_input}")
    print(f"[history]{history}")
    # TODO: 从命令行参数中获取
    enable_chat = True

    ans = SALES_BOT({"query": user_input})
    # 如果检索出结果，或者开了大模型聊天模式
    # 返回 RetrievalQA combine_documents_chain 整合的结果
    if ans["source_documents"] or enable_chat:
        print(f"[result]{ans['result']}")
        print(f"[source_documents]{ans['source_documents']}")
        if len(ans['source_documents']) == 0 :
            role_reminder = "你是中国顶级的航运产品销售负责人。"
            messages = [(None, role_reminder)] + \
                       [("user", message) for message in history] + \
                       [("user", f"问题：{user_input}")]
            prompt = ChatPromptTemplate.from_messages(messages)
            LLM = ChatOpenAI(temperature=0,model_name="gpt-4", base_url="https://api.xiaoai.plus/v1", api_key="sk-tdqfro61NniG2LZd5394E5F28c51419d8b4dE7Db5a6105C4")
            
            try:
                chat = prompt.format_messages(message=user_input)
                chat_result = LLM.invoke(chat)
                return chat_result.content
            except Exception as e:
                print(f"Error invoking OpenAI API: {e}")
                return "Error processing your request"
        else:
            return ans["result"]
    # 否则输出套路话术
    else:
        return "这个问题我要问问领导"
    

def launch_gradio():
    demo = gr.ChatInterface(
        fn=sales_chat,
        title="航运产品销售",
        # retry_btn=None,
        # undo_btn=None,
        chatbot=gr.Chatbot(height=600),
    )

    demo.launch(share=True, server_name="0.0.0.0")

if __name__ == "__main__":
    initialize_sales_bot()
    if len(sys.argv) > 1 and sys.argv[1].lower() == "false":
        enable_chat = False
    else:
        enable_chat = True
    launch_gradio()
