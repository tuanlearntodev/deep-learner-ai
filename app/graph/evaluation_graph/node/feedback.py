from app.graph.evaluation_graph.chain import feedback_generator
from app.graph.evaluation_graph.state import GraphState


def generate_feedback(state: GraphState) -> dict:
    """Generate personalized feedback based on the evaluation and course materials."""
    print("---GENERATE FEEDBACK---")
    
    question = state["question"]
    user_answer = state["user_answer"]
    correct_answer = state["correct_answer"]
    evaluation = state["evaluation"]
    score = state["score"]
    documents = state.get("documents", [])
    
    # Format documents as context
    if documents:
        context = "\n\n".join([f"Document {i+1}:\n{doc}" for i, doc in enumerate(documents)])
        print(f"📚 Using {len(documents)} documents for feedback context")
    else:
        context = "No specific course materials available."
        print("⚠️ No documents available for context")
    
    # Generate detailed feedback with context
    feedback_result = feedback_generator.invoke({
        "question": question,
        "user_answer": user_answer,
        "correct_answer": correct_answer,
        "evaluation": evaluation,
        "score": score,
        "context": context
    })
    
    feedback = feedback_result.content if hasattr(feedback_result, 'content') else str(feedback_result)
    
    print(f"Feedback: {feedback[:100]}...")
    
    return {
        "feedback": feedback
    }
