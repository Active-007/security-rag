"""
    提示词模板：rag_qa/core/prompts
"""
# 导入 PromptTemplate 类，用于创建 Prompt 模板
from langchain_core.prompts import PromptTemplate


# 定义 RAGPrompts 类，用于管理所有 Prompt 模板
class RAGPrompts:

    # 定义 RAG 提示模板
    @staticmethod
    def rag_prompt():
        return PromptTemplate(
            template="""
        你是安保集团企业知识库智能助手，负责帮助员工解答安保执勤和武装押运相关的制度问题。请按照以下步骤处理：

        1. **分析问题和上下文**：
           - 基于提供的制度文档上下文（如果有）和你的知识回答问题。
           - 如果答案来源于检索到的制度文档，请在回答中明确说明，例如："根据集团制度规定，……"。
           - 涉及具体数字、流程步骤、制度条款时，请严格依据上下文内容，不要编造。

        2. **评估对话历史**：
           - 检查对话历史是否与当前问题相关（例如，是否涉及相同的制度条款、业务流程或操作规范）。
           - 如果对话历史与问题相关，请结合历史信息生成更准确的回答。
           - 如果对话历史无关（例如，仅包含问候或不相关的内容），忽略历史，仅基于上下文和问题回答。

        3. **生成回答**：
           - 提供清晰、准确的回答，使用规范的制度用语，避免模糊表述。
           - 如果上下文和历史消息均不足以回答问题，请回复："信息不足，无法准确回答，请联系合规部门或客服热线：{phone}。"

        **制度文档上下文**: {context}
        **对话历史**:
        {history}
        **问题**: {question}

        **回答**:
        """,
            input_variables=["context", "history", "question", "phone"],
        )

    # 定义假设问题生成的 Prompt 模板
    @staticmethod
    def hyde_prompt():
        #   创建并返回 PromptTemplate 对象
        return PromptTemplate(
            template="""  
            假设你是安保集团员工，想了解以下制度问题，请生成一个简短的假设答案：  
            问题: {query}  
            假设答案：  
            """,
            #   定义输入变量
            input_variables=["query"],
        )

    #   定义子查询生成的 Prompt 模板
    @staticmethod
    def subquery_prompt():
        #   创建并返回 PromptTemplate 对象
        return PromptTemplate(
            template="""  
            将以下安保制度相关的复杂查询分解为多个简单子查询，每行一个子查询：  
            查询: {query}  
            子查询:  
            """,
            #   定义输入变量
            input_variables=["query"],
        )

    #   定义回溯问题生成的 Prompt 模板
    @staticmethod
    def backtracking_prompt():
        #   创建并返回 PromptTemplate 对象
        return PromptTemplate(
            template="""  
            将以下安保制度相关的复杂查询简化为一个更简单的问题：  
            查询: {query}  
            简化问题:  
            """,
            #   定义输入变量
            input_variables=["query"],
        )
