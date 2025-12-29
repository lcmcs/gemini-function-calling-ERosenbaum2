"""
Gemini API client with function calling support.
Handles the interaction between user prompts, Gemini, and function calls.
"""
import google.generativeai as genai
from typing import List, Dict, Any, Optional
from config import GEMINI_API_KEY, GEMINI_MODEL
from functions import get_gemini_functions, execute_function


class GeminiFunctionCallingClient:
    """Client for interacting with Gemini API with function calling."""
    
    def __init__(self):
        """Initialize the Gemini client with API key and model."""
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            tools=[{"function_declarations": get_gemini_functions()}]
        )
        self.chat = None
        self.conversation_history = []
    
    def start_chat(self):
        """Start a new chat session."""
        self.chat = self.model.start_chat(enable_automatic_function_calling=False)
        self.conversation_history = []
    
    def send_message(self, user_message: str, verbose: bool = True) -> Dict[str, Any]:
        """
        Send a message to Gemini and handle function calls.
        
        Args:
            user_message: The user's message/prompt
            verbose: Whether to print detailed information about the flow
        
        Returns:
            Dictionary containing the response and flow information
        """
        if not self.chat:
            self.start_chat()
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"USER: {user_message}")
            print(f"{'='*60}\n")
        
        # Send message to Gemini
        response = self.chat.send_message(user_message)
        
        flow_info = {
            'user_message': user_message,
            'function_calls': [],
            'api_responses': [],
            'final_response': None
        }
        
        # Handle function calls if present
        # Check if response contains function calls
        while (hasattr(response, 'candidates') and 
               len(response.candidates) > 0 and
               hasattr(response.candidates[0], 'content') and
               hasattr(response.candidates[0].content, 'parts') and
               len(response.candidates[0].content.parts) > 0 and
               hasattr(response.candidates[0].content.parts[0], 'function_call') and
               response.candidates[0].content.parts[0].function_call):
            
            function_call = response.candidates[0].content.parts[0].function_call
            function_name = function_call.name
            # Convert function_call.args to dictionary
            # The args can be a dict, protobuf Struct, or other format
            function_args = {}
            if hasattr(function_call, 'args') and function_call.args:
                args_obj = function_call.args
                # Handle different arg formats
                if isinstance(args_obj, dict):
                    function_args = args_obj
                elif hasattr(args_obj, '__dict__'):
                    function_args = {k: v for k, v in args_obj.__dict__.items() 
                                   if not k.startswith('_')}
                else:
                    # Try protobuf conversion if available
                    try:
                        from google.protobuf.json_format import MessageToDict
                        if hasattr(args_obj, 'SerializeToString'):
                            function_args = MessageToDict(args_obj, preserving_proto_field_name=True)
                    except (ImportError, AttributeError):
                        # Fallback: try direct conversion
                        try:
                            function_args = dict(args_obj) if args_obj else {}
                        except (TypeError, ValueError):
                            function_args = {}
            
            if verbose:
                print(f"🔧 GEMINI FUNCTION CALL:")
                print(f"   Function: {function_name}")
                print(f"   Arguments: {function_args}\n")
            
            flow_info['function_calls'].append({
                'name': function_name,
                'arguments': function_args
            })
            
            # Execute the function
            function_result = execute_function(function_name, function_args)
            
            if verbose:
                print(f"📡 API REQUEST:")
                if function_name == 'createBroadcast':
                    print(f"   POST {self._get_api_url('/broadcasts')}")
                    print(f"   Body: {function_args}\n")
                elif function_name == 'findNearbyBroadcasts':
                    print(f"   GET {self._get_api_url('/broadcasts/nearby')}")
                    print(f"   Query Params: {function_args}\n")
            
            if verbose:
                print(f"📥 API RESPONSE:")
                if function_result['success']:
                    print(f"   Status: Success")
                    print(f"   Data: {function_result['data']}\n")
                else:
                    print(f"   Status: Error")
                    print(f"   Error: {function_result.get('error', 'Unknown error')}\n")
            
            flow_info['api_responses'].append({
                'function_name': function_name,
                'success': function_result['success'],
                'data': function_result.get('data'),
                'error': function_result.get('error')
            })
            
            # Create function response for Gemini
            # Format: dictionary with function_response containing name and response
            function_response_data = {
                'function_response': {
                    'name': function_name,
                    'response': function_result.get('data') if function_result['success'] else {
                        'error': function_result.get('error', 'Unknown error')
                    }
                }
            }
            
            # Send function response back to Gemini
            # Include the original response content along with the function response
            response = self.chat.send_message([
                response.candidates[0].content,
                function_response_data
            ])
        
        # Get final text response
        final_text = response.text if hasattr(response, 'text') else str(response)
        
        if verbose:
            print(f"💬 GEMINI FINAL RESPONSE:")
            print(f"   {final_text}\n")
            print(f"{'='*60}\n")
        
        flow_info['final_response'] = final_text
        
        return flow_info
    
    def _get_api_url(self, endpoint: str) -> str:
        """Get full API URL for an endpoint."""
        from config import MINYAN_API_BASE_URL
        return f"{MINYAN_API_BASE_URL}{endpoint}"
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation flow."""
        summary = "Conversation Flow Summary:\n"
        summary += "=" * 60 + "\n\n"
        
        for i, entry in enumerate(self.conversation_history, 1):
            summary += f"Exchange {i}:\n"
            summary += f"  User: {entry['user_message']}\n"
            
            if entry['function_calls']:
                summary += f"  Function Calls:\n"
                for fc in entry['function_calls']:
                    summary += f"    - {fc['name']}({fc['arguments']})\n"
            
            if entry['api_responses']:
                summary += f"  API Responses:\n"
                for ar in entry['api_responses']:
                    status = "✓ Success" if ar['success'] else "✗ Error"
                    summary += f"    - {ar['function_name']}: {status}\n"
            
            summary += f"  Gemini: {entry['final_response'][:100]}...\n\n"
        
        return summary

