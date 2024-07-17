import gradio as gr
import sys
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
enable_chat=True

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

def sales_chat(user_input, history):
    print(f"[message]{user_input}")
    print(f"[history]{history}")


    formatted_history = "\n".join([f"客戶: {h[0]}\n銷售助理: {h[1]}" for h in history])

    ans = SALES_BOT({"query": user_input, "chat_history": formatted_history})
    # 如果检索出结果，或者开了大模型聊天模式
    # 返回 RetrievalQA combine_documents_chain 整合的结果
    if ans["source_documents"] or enable_chat:
        print(f"[result]{ans['result']}")
        print(f"[source_documents]{ans['source_documents']}")
        if len(ans['source_documents']) == 0 :
            template = """
            你是一个中国顶级的航运产品销售负责人。你的回答应该自然、友好，并且要有连贯性。请记住以下几点：
            总是要理解并回应客户最新的问题，同时考虑之前的对话内容。
            如果客户只提供简短的回答，试着根据上下文推断他们的意思。
            避免重复提问，除非真的需要澄清。
            用自然的语气交谈，就像真人一样。避免过于正式或机械的表达。
            如果不确定，可以做出合理的假设，并在回答中体现出来。
            不要提及你是一个大模型的概念以及语气。
            以下是之前的对话：
            {history}
            客戶的最新回答是：{question}
            请给出一个自然、连贯的回复，要像真人销售助理一样：
            """

            
            llm = ChatOpenAI(model_name="gpt-4", temperature=0, base_url="https://api.xiaoai.plus/v1",api_key="sk-tdqfro61NniG2LZd5394E5F28c51419d8b4dE7Db5a6105C4")

            prompt = PromptTemplate(template=template, input_variables=["history", "question"])
            chain = LLMChain(llm=llm, prompt=prompt)

            response = chain.run(history=formatted_history, question=user_input)

            return response    
        else:
            return ans["result"]
    # 否则输出套路话术
    else:
        return "我是顶级的，所以你等等，我编一下"
    

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
    print(f"[enable chat]{enable_chat}")
    launch_gradio()
