from app.graph.main_graph.state import AgentState
from app.graph.evaluation_graph import evaluation_graph, GraphState as EvaluationState
from langchain_core.messages import AIMessage
import json


def node_evaluation_bridge(state: AgentState):
    """
    Bridge node that invokes the evaluation graph.
    Extracts question from last AI message and user's answer from current message.
    Uses RAG pipeline to get correct answer and evaluate.
    """
    print("---MAIN GRAPH: Evaluation Bridge Node---")
    
    # Extract the last user message as the answer
    last_message = state["messages"][-1]
    user_answer = last_message.content
    workspace_id = state["workspace_id"]
    subject = state.get("subject", "general learning")
    web_search = state.get("web_search", False)
    crag = state.get("crag", False)  # Use False as default to match main graph
    
    # Find the last AI message (the question)
    question = ""
    ai_message_content = ""
    
    for i in range(len(state["messages"]) - 2, -1, -1):
        msg = state["messages"][i]
        # Check if it's an AI message
        if hasattr(msg, 'type') and msg.type == 'ai':
            ai_message_content = msg.content
            break
        elif not hasattr(msg, 'type'):  # AIMessage class check
            # Check if it's AIMessage by class name
            if msg.__class__.__name__ == 'AIMessage':
                ai_message_content = msg.content
                break
    
    if not ai_message_content:
        print("⚠️ No previous AI message found - treating user message as standalone answer to evaluate")
        # Treat the user message as an explanation/answer to evaluate
        # Extract the answer part (before "evaluate" or "->")
        answer_to_evaluate = user_answer
        
        # Check for "evaluate" or "->" separator
        if " -> evaluate" in answer_to_evaluate.lower():
            answer_to_evaluate = answer_to_evaluate.split("->")[0].strip()
        elif "→ evaluate" in answer_to_evaluate.lower():
            answer_to_evaluate = answer_to_evaluate.split("→")[0].strip()
        elif answer_to_evaluate.lower().endswith(" evaluate"):
            answer_to_evaluate = answer_to_evaluate[:-8].strip()
        
        print(f"📝 Evaluating standalone explanation: {answer_to_evaluate[:100]}...")
        
        # Prepare evaluation graph state - no specific question, just evaluate the explanation
        evaluation_state: EvaluationState = {
            "question": "Evaluate this explanation/answer based on the subject context",
            "user_answer": answer_to_evaluate,
            "correct_answer": "",
            "workspace_id": workspace_id,
            "subject": subject,
            "evaluation": "",
            "score": 0.0,
            "feedback": "",
            "documents": [],
            "web_search": web_search,
            "crag": crag
        }
        
        # Invoke the evaluation graph
        result = evaluation_graph.invoke(evaluation_state)
        
        # Format response as single evaluation
        response_content = json.dumps({
            "evaluations": [{
                "question": f"Explanation about {subject}",
                "user_answer": result.get("user_answer", answer_to_evaluate),
                "correct_answer": result.get("correct_answer", ""),
                "score": result.get("score", 0.0),
                "evaluation": result.get("evaluation", ""),
                "feedback": result.get("feedback", "")
            }],
            "overall_score": result.get("score", 0.0),
            "total_questions": 1,
            "response_type": "evaluation"
        }, ensure_ascii=False)
        
        return {
            "messages": [AIMessage(
                content=response_content,
                additional_kwargs={"response_type": "evaluation"}
            )]
        }
    
    # Parse the AI message to extract questions
    try:
        parsed = json.loads(ai_message_content)
        if isinstance(parsed, list) and len(parsed) > 0:
            # It's a quiz array, can't evaluate against this
            print("⚠️ Previous message was a quiz, not open-ended questions")
            return {
                "messages": [AIMessage(content="I can evaluate answers to open-ended questions. For quizzes, please use the quiz interface. Try asking me a question first!")]
            }
    except (json.JSONDecodeError, TypeError):
        # Not JSON, it's regular text
        pass
    
    # Extract all questions from AI message
    questions = []
    
    # Check if it's a list of generated questions (numbered list)
    if any(line.strip().startswith(('1.', '1)', '1 -')) for line in ai_message_content.split('\n')):
        print("📝 Detected numbered question list from AI")
        lines = ai_message_content.split('\n')
        current_question = ""
        
        for line in lines:
            line_stripped = line.strip()
            # Check if line starts with a number
            if any(line_stripped.startswith(f'{i}.') or line_stripped.startswith(f'{i})') or line_stripped.startswith(f'{i} -') for i in range(1, 20)):
                # Save previous question if exists
                if current_question:
                    questions.append(current_question.strip())
                # Start new question (remove number prefix)
                current_question = line_stripped.split('.', 1)[-1].split(')', 1)[-1].split('-', 1)[-1].strip()
            elif current_question and line_stripped:
                # Continue multi-line question
                current_question += " " + line_stripped
        
        # Add last question
        if current_question:
            questions.append(current_question.strip())
        
        print(f"📌 Extracted {len(questions)} questions")
    else:
        # Single question
        questions = [ai_message_content.strip()]
    
    if not questions:
        print("⚠️ No questions found")
        return {
            "messages": [AIMessage(content="I couldn't find any questions to evaluate. Please ask questions first!")]
        }
    
    # Parse user's answers (assume they're separated by newlines or numbered)
    user_answers = []
    user_answer_lines = user_answer.split('\n')
    
    # Try to detect if user numbered their answers
    numbered_answers = []
    current_answer = ""
    
    for line in user_answer_lines:
        line_stripped = line.strip()
        if any(line_stripped.startswith(f'{i}.') or line_stripped.startswith(f'{i})') or line_stripped.startswith(f'{i} -') for i in range(1, 20)):
            if current_answer:
                numbered_answers.append(current_answer.strip())
            current_answer = line_stripped.split('.', 1)[-1].split(')', 1)[-1].split('-', 1)[-1].strip()
        elif current_answer and line_stripped:
            current_answer += " " + line_stripped
        elif not current_answer and line_stripped:
            # If no number found yet, start collecting
            current_answer = line_stripped
    
    if current_answer:
        numbered_answers.append(current_answer.strip())
    
    # Use numbered answers if found, otherwise treat entire answer as single response
    if len(numbered_answers) > 0:
        user_answers = numbered_answers
    else:
        # If multiple questions but single answer, repeat it for all
        user_answers = [user_answer.strip()] * len(questions)
    
    # Make sure we have matching answers for questions
    while len(user_answers) < len(questions):
        user_answers.append("No answer provided")
    
    print(f"💬 Found {len(user_answers)} user answers for {len(questions)} questions")
    print(f"🌐 Web search: {web_search}, CRAG: {crag}")
    
    # Evaluate each question-answer pair
    evaluations = []
    
    for idx, (question, user_ans) in enumerate(zip(questions, user_answers), 1):
        print(f"\n🔄 Evaluating question {idx}/{len(questions)}")
        print(f"   Question: {question[:80]}...")
        print(f"   Answer: {user_ans[:80]}...")
        
        # Prepare evaluation graph state
        evaluation_state: EvaluationState = {
            "question": question,
            "user_answer": user_ans,
            "correct_answer": "",
            "workspace_id": workspace_id,
            "subject": subject,
            "evaluation": "",
            "score": 0.0,
            "feedback": "",
            "documents": [],
            "web_search": web_search,
            "crag": crag
        }
        
        # Invoke the evaluation graph
        result = evaluation_graph.invoke(evaluation_state)
        
        # Extract results
        evaluations.append({
            "question": result.get("question", question),
            "user_answer": result.get("user_answer", user_ans),
            "correct_answer": result.get("correct_answer", ""),
            "score": result.get("score", 0.0),
            "evaluation": result.get("evaluation", ""),
            "feedback": result.get("feedback", "")
        })
        
        print(f"   ✅ Score: {result.get('score', 0.0)}")
    
    # Calculate overall score
    overall_score = sum(e["score"] for e in evaluations) / len(evaluations) if evaluations else 0.0
    print(f"\n✅ All evaluations complete - Overall Score: {overall_score:.2f}")
    
    # Format response as JSON with all evaluations
    response_content = json.dumps({
        "evaluations": evaluations,
        "overall_score": overall_score,
        "total_questions": len(questions),
        "response_type": "evaluation"
    }, ensure_ascii=False)
    
    return {
        "messages": [AIMessage(
            content=response_content,
            additional_kwargs={"response_type": "evaluation"}
        )]
    }
