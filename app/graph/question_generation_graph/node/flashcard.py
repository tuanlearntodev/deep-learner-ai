from typing import Any, Dict
import json
import re
from app.graph.question_generation_graph.state import QuestionGraphState
from app.graph.question_generation_graph.chain.flashcard import flashcard_chain


def extract_question_count(prompt: str, default: int = 7) -> int:
    """Extract the number of questions/cards requested from the user prompt."""
    # Look for patterns like "5 flashcards", "10 cards", "generate 3 flashcards", etc.
    patterns = [
        r'(\d+)\s*(?:flash)?cards?',  # "5 flashcards" or "5 cards"
        r'(\d+)\s*questions?',  # "5 questions"
        r'quiz\s+(?:me\s+)?(?:with\s+)?(\d+)',  # "quiz me with 5"
        r'generate\s+(\d+)',  # "generate 5"
        r'create\s+(\d+)',  # "create 5"
        r'give\s+(?:me\s+)?(\d+)',  # "give me 5"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, prompt.lower())
        if match:
            count = int(match.group(1))
            # Validate the count (between 1 and 20 to be reasonable)
            if 1 <= count <= 20:
                print(f"📊 Detected request for {count} flashcards")
                return count
    
    print(f"📊 No specific count found, using default: {default} flashcards")
    return default


def generate_flashcards(state: QuestionGraphState) -> Dict[str, Any]:
    print("--Generate Flashcards---")
    question = state["question"]  # This is the topic/subject
    documents = state["documents"]
    
    # Extract the number of flashcards from the user's prompt
    num_questions = extract_question_count(question, default=7)

    try:
        # Invoke the chain with format_instructions
        from langchain_core.output_parsers import JsonOutputParser
        from app.graph.question_generation_graph.chain.flashcard import Flashcard
        
        parser = JsonOutputParser(pydantic_object=Flashcard)
        format_instructions = parser.get_format_instructions()
        
        result = flashcard_chain.invoke({
            "question": question, 
            "context": documents,
            "format_instructions": format_instructions,
            "num_questions": num_questions
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
            
        print(f"✅ Generated {len(result) if isinstance(result, list) else 1} flashcards")
        
    except Exception as e:
        print(f"❌ Error generating flashcards: {e}")
        generation = json.dumps([])
        answer_found = False
    
    return {
        "documents": documents, 
        "question": question, 
        "generation": generation, 
        "answer_found": answer_found
    }
