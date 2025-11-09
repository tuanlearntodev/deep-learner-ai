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
        response_type = "text"
    else:
        # Detect if it's JSON (quiz format) or plain text (open-ended questions)
        import json
        try:
            parsed = json.loads(generation)
            if isinstance(parsed, list) and len(parsed) > 0:
                # Check if it's quiz format (has type, question, options, correctAnswer)
                if all(key in parsed[0] for key in ["type", "question", "options", "correctAnswer"]):
                    response_type = "quiz"
                else:
                    response_type = "questions"
            else:
                response_type = "text"
        except (json.JSONDecodeError, KeyError, IndexError):
            # Plain text questions
            response_type = "questions"
    
    # Create AI message with the generated questions and metadata
    ai_message = AIMessage(
        content=generation,
        additional_kwargs={"response_type": response_type}
    )
    
    print(f"✅ Question Generation Complete (type: {response_type})")
    
    return {
        "messages": [ai_message]
    }
