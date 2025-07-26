from abc import ABC, abstractmethod

class BaseAgent(ABC):
    @abstractmethod
    def run(self, input_text: str) -> str:
        """Run the agent on the input text and return a response."""
        pass

class ReActAgent(BaseAgent):
    def run(self, input_text: str) -> str:
        # Simple demo: calculator tool
        if "calculate" in input_text.lower():
            expr = input_text.lower().replace("calculate", "").strip()
            try:
                result = eval(expr, {"__builtins__": {}})
                return f"Result: {result}"
            except Exception as e:
                return f"Error: {str(e)}"
        return "Sorry, I can only calculate for now."
    
    def reason_and_act(self, user_input: str) -> dict:
        # Simple demo: calculator tool
        if "calculate" in user_input.lower():
            expr = user_input.lower().replace("calculate", "").strip()
            try:
                result = eval(expr, {"__builtins__": {}})
                return {
                    "thought": "I need to calculate.",
                    "action": "calculator",
                    "result": f"Result: {result}"
                }
            except Exception as e:
                return {
                    "thought": "Tried to calculate but failed.",
                    "action": "calculator",
                    "result": f"Error: {str(e)}"
                }
        return {
            "thought": "I don't know how to handle this.",
            "action": None,
            "result": "Sorry, I can only calculate for now."
        }