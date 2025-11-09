from app.graph.evaluation_graph.chain import answer_evaluator
from app.graph.evaluation_graph.state import GraphState


def evaluate_answer(state: GraphState) -> dict:
    """Evaluate the user's answer against the correct answer using retrieved documents."""
    print("---EVALUATE ANSWER---")
    
    question = state["question"]
    user_answer = state["user_answer"]
    correct_answer = state["correct_answer"]
    documents = state.get("documents", [])
    
    # Format documents as context
    if documents:
        context = "\n\n".join([f"Document {i+1}:\n{doc}" for i, doc in enumerate(documents)])
        print(f"📚 Using {len(documents)} documents for evaluation context")
    else:
        context = "No specific course materials available. Evaluate based on general knowledge."
        print("⚠️ No documents available for context")
    
    # Call the evaluator chain with context
    result = answer_evaluator.invoke({
        "question": question,
        "user_answer": user_answer,
        "correct_answer": correct_answer,
        "context": context
    })
    
    print(f"Score: {result.score}")
    print(f"Correctness: {result.correctness}")
    print(f"Explanation: {result.explanation}")
    
    return {
        "score": result.score,
        "evaluation": result.correctness,
        "feedback": result.explanation
    }
