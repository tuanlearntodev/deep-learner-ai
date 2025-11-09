from typing import Any, Dict
from langchain_core.messages import AIMessage
from app.graph.main_graph.state import AgentState
from app.graph.question_generation_graph.state import QuestionGraphState
from app.graph.question_generation_graph import question_generation_graph


def node_question_generation_bridge(state: AgentState) -> Dict[str, Any]:
    """
    Bridge between main graph AgentState and question generation graph QuestionGraphState.
    Routes to question generation graph for generating questions/quizzes.
    """
    print("---MAIN GRAPH: Question Generation Bridge Node---")
    
    # Extract the latest message
    messages = state.get("messages", [])
    last_message = messages[-1] if messages else None
    question = last_message.content if last_message else ""
    
    # Get other state variables
    workspace_id = state.get("workspace_id", "")
    web_search = state.get("web_search", False)
    crag = state.get("crag", True)
    subject = state.get("subject", "general learning")
    
    print(f"Question/Topic: {question}")
    print(f"Workspace ID: {workspace_id}")
    print(f"Subject: {subject}")
    
    # Create question generation state
    question_state = QuestionGraphState(
        question=question,
        generation="",
        web_search=web_search,
        crag=crag,
        documents=[],
        answer_found=True,
        subject=subject,
        workspace_id=workspace_id
    )
    
    # Invoke question generation graph
    result = question_generation_graph.invoke(question_state)
    
    # Extract generated questions/quiz
    generation = result.get("generation", "")
    answer_found = result.get("answer_found", False)
    
    if not answer_found:
        generation = "I don't have enough information in the documents to generate meaningful questions about this topic."
    
    # Create AI message with the generated questions
    ai_message = AIMessage(content=generation)
    
    print(f"✅ Question Generation Complete")
    
    return {
        "messages": [ai_message]
    }
