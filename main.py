"""
Main entry point for Gemini Function Calling demonstration.
Interactive CLI that demonstrates complete request/response flow.
"""
import sys
from gemini_client import GeminiFunctionCallingClient


def print_welcome():
    """Print welcome message and instructions."""
    print("\n" + "="*60)
    print("  Gemini Function Calling - Minyan Finder API Demo")
    print("="*60)
    print("\nThis demo shows how Gemini can call your API functions.")
    print("You can interact naturally, and Gemini will use function calling")
    print("to interact with the Minyan Finder API.\n")
    print("Example prompts:")
    print("  - 'I need a mincha minyan at 40.7128, -74.0060 between 1pm and 2pm today'")
    print("  - 'Find nearby mincha minyans within 2 miles of 40.7130, -74.0059'")
    print("  - 'Create a broadcast for shacharit at 34.0522, -118.2437'")
    print("\nType 'quit' or 'exit' to end the session.")
    print("Type 'examples' to see example prompts.")
    print("="*60 + "\n")


def print_examples():
    """Print example prompts."""
    print("\n" + "="*60)
    print("Example Prompts:")
    print("="*60)
    print("\n1. Create Broadcast:")
    print("   'I need a mincha minyan at 40.7128, -74.0060'")
    print("   'Create a broadcast for maariv at latitude 34.0522, longitude -118.2437'")
    print("   'I'm looking for a shacharit minyan at 40.7580, -73.9855'")
    print("\n2. Find Nearby Broadcasts:")
    print("   'Find nearby mincha minyans within 2 miles'")
    print("   'Search for minyans near 40.7130, -74.0059'")
    print("   'Are there any shacharit minyans nearby?'")
    print("\n3. Combined:")
    print("   'I need a mincha minyan. Can you create one and then find others nearby?'")
    print("="*60 + "\n")


def run_interactive_demo():
    """Run the interactive demonstration."""
    try:
        client = GeminiFunctionCallingClient()
        client.start_chat()
        
        print_welcome()
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye! Thanks for trying the demo.\n")
                    break
                
                if user_input.lower() == 'examples':
                    print_examples()
                    continue
                
                # Send message and get response
                flow_info = client.send_message(user_input, verbose=True)
                
                # Store in conversation history
                client.conversation_history.append(flow_info)
                
            except KeyboardInterrupt:
                print("\n\nGoodbye! Thanks for trying the demo.\n")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
                print("Please try again or type 'quit' to exit.\n")
    
    except Exception as e:
        print(f"\n❌ Failed to initialize Gemini client: {e}\n")
        print("Please check your GEMINI_API_KEY in the .env file.\n")
        sys.exit(1)


def run_example_demo():
    """Run a scripted demonstration with predefined examples."""
    print("\n" + "="*60)
    print("  Running Scripted Demo")
    print("="*60 + "\n")
    
    try:
        client = GeminiFunctionCallingClient()
        client.start_chat()
        
        examples = [
            {
                'prompt': "I need a mincha minyan at 40.7128, -74.0060. The earliest time is 2025-03-26T13:00:00Z and latest is 2025-03-26T14:00:00Z",
                'description': "Example 1: Creating a broadcast"
            },
            {
                'prompt': "Find nearby mincha minyans within 2 miles of latitude 40.7130 and longitude -74.0059",
                'description': "Example 2: Finding nearby broadcasts"
            }
        ]
        
        for i, example in enumerate(examples, 1):
            print(f"\n{'='*60}")
            print(f"Example {i}: {example['description']}")
            print(f"{'='*60}\n")
            
            flow_info = client.send_message(example['prompt'], verbose=True)
            client.conversation_history.append(flow_info)
            
            if i < len(examples):
                input("\nPress Enter to continue to next example...")
        
        print("\n" + "="*60)
        print("Demo completed!")
        print("="*60 + "\n")
    
    except Exception as e:
        print(f"\n❌ Error during demo: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--examples':
        run_example_demo()
    else:
        run_interactive_demo()

