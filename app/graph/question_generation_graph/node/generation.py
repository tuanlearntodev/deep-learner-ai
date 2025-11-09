from typing import Any, Dict
from app.graph.question_generation_graph.state import QuestionGraphState
from app.graph.question_generation_graph.chain.generation import generation_chain


def generate_questions(state: QuestionGraphState) -> Dict[str, Any]:
    print("--Generate Questions---")
    question = state["question"]  # This is the topic/subject
    documents = state["documents"]

    generation = generation_chain.invoke({"question": question, "context": documents})
    
    # Check if questions were successfully generated
    answer_found = "not enough context" not in generation.lower()
    
    return {"documents": documents, "question": question, "generation": generation, "answer_found": answer_found}
