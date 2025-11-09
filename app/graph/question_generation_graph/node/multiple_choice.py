from typing import Any, Dict
import json
from app.graph.question_generation_graph.state import QuestionGraphState
from app.graph.question_generation_graph.chain.multiple_choice import multiple_choice_chain


def generate_multiple_choice(state: QuestionGraphState) -> Dict[str, Any]:
    print("--Generate Multiple Choice Questions---")
    question = state["question"]  # This is the topic/subject
    documents = state["documents"]

    try:
        # Invoke the chain with format_instructions
        from langchain_core.output_parsers import JsonOutputParser
        from app.graph.question_generation_graph.chain.multiple_choice import MultipleChoiceQuestion
        
        parser = JsonOutputParser(pydantic_object=MultipleChoiceQuestion)
        format_instructions = parser.get_format_instructions()
        
        result = multiple_choice_chain.invoke({
            "question": question, 
            "context": documents,
            "format_instructions": format_instructions
        })
        
        # Convert result to JSON string for storage
        if isinstance(result, list):
            generation = json.dumps(result, indent=2)
            answer_found = len(result) > 0
        elif isinstance(result, dict):
            generation = json.dumps([result], indent=2)
            answer_found = True
        else:
            generation = str(result)
            answer_found = False
            
        print(f"✅ Generated {len(result) if isinstance(result, list) else 1} multiple choice questions")
        
    except Exception as e:
        print(f"❌ Error generating multiple choice questions: {e}")
        generation = json.dumps([])
        answer_found = False
    
    return {
        "documents": documents, 
        "question": question, 
        "generation": generation, 
        "answer_found": answer_found
    }
