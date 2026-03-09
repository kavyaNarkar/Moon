from ..core.brain import query_llm
from ..core.parser import parse_command
from ..core.executor import execute_task
from ..utils.logger import logger

def start_terminal_mode():
    """
    Main loop for direct interaction via the terminal.
    """
    print("\n--- Moon AI Assistant: Text Mode ---")
    print("Type 'exit' to quit.")
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("Goodbye!")
                break
                
            if not user_input:
                continue
                
            logger.info(f"User typed: {user_input}")
            
            # 1. Try Fast Track (Rule-based)
            from ..core.parser import quick_parse
            command = quick_parse(user_input)
            
            if not command:
                # 2. Fallback to LLM
                llm_response = query_llm(user_input)
                command = parse_command(llm_response)
            else:
                logger.info("Fast track triggered.")
            
            # 3. Execute
            response = execute_task(command)
            
            # 4. Display response
            print(f"\n{response}")
            
        except KeyboardInterrupt:
            print("\nExiting terminal mode...")
            break
        except Exception as e:
            logger.error(f"Error in terminal mode: {e}")
            print(f"An error occurred: {e}")
