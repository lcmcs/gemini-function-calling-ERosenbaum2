# Gemini Function Calling Demo - Minyan Finder API

This demonstration shows how to use Google's Gemini API with function calling to interact with the Minyan Finder API. Gemini can intelligently call your API functions based on natural language user input.

## Overview

The demo implements two function calls:
1. **createBroadcast** - Creates a new minyan broadcast
2. **findNearbyBroadcasts** - Searches for nearby minyan broadcasts

The complete request/response flow is demonstrated:
- User provides natural language input
- Gemini determines which function(s) to call
- Function handlers make HTTP requests to the Minyan Finder API
- API responses are returned to Gemini
- Gemini provides a natural language response to the user

## Prerequisites

- Python 3.8 or higher
- Google AI Studio account (for Gemini API key)
- Access to the Minyan Finder API (local or remote)

## Setup Instructions

### 1. Get a Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
MINYAN_API_BASE_URL=http://localhost:5000
GEMINI_MODEL=gemini-1.5-flash
```

**Note:** If your Minyan Finder API is deployed elsewhere, update `MINYAN_API_BASE_URL` accordingly.

### 4. Ensure Minyan Finder API is Running

Make sure your Minyan Finder API is accessible at the URL specified in `MINYAN_API_BASE_URL`. If running locally, start the API server first.

## Usage

### Interactive Mode (Default)

Run the interactive CLI:

```bash
python main.py
```

This starts an interactive session where you can chat with Gemini. Type natural language prompts, and Gemini will call the appropriate API functions.

**Example prompts:**
- "I need a mincha minyan at 40.7128, -74.0060"
- "Find nearby mincha minyans within 2 miles of 40.7130, -74.0059"
- "Create a broadcast for shacharit at 34.0522, -118.2437"

Type `quit` or `exit` to end the session.

### Scripted Demo Mode

Run predefined examples:

```bash
python main.py --examples
```

This runs through two example scenarios demonstrating both function calls.

## Understanding the Flow

### Example 1: Creating a Broadcast

**User Input:**
```
I need a mincha minyan at 40.7128, -74.0060
```

**Flow:**
1. Gemini analyzes the user's request
2. Gemini calls `createBroadcast` function with parsed parameters
3. Program makes POST request to `/broadcasts` endpoint
4. API returns broadcast ID and confirmation
5. Gemini responds with a user-friendly message

**Output:**
```
USER: I need a mincha minyan at 40.7128, -74.0060

🔧 GEMINI FUNCTION CALL:
   Function: createBroadcast
   Arguments: {'latitude': 40.7128, 'longitude': -74.0060, 'minyanType': 'mincha', ...}

📡 API REQUEST:
   POST http://localhost:5000/broadcasts
   Body: {...}

📥 API RESPONSE:
   Status: Success
   Data: {'id': 'abc123-def456-ghi789', 'message': 'Broadcast created successfully'}

💬 GEMINI FINAL RESPONSE:
   I've created a mincha minyan broadcast for you at the specified location...
```

### Example 2: Finding Nearby Broadcasts

**User Input:**
```
Find nearby mincha minyans within 2 miles of 40.7130, -74.0059
```

**Flow:**
1. Gemini identifies the search request
2. Gemini calls `findNearbyBroadcasts` function
3. Program makes GET request to `/broadcasts/nearby` with query parameters
4. API returns list of nearby broadcasts
5. Gemini formats and presents the results

**Output:**
```
USER: Find nearby mincha minyans within 2 miles of 40.7130, -74.0059

🔧 GEMINI FUNCTION CALL:
   Function: findNearbyBroadcasts
   Arguments: {'latitude': 40.7130, 'longitude': -74.0059, 'radius': 2, 'minyanType': 'mincha'}

📡 API REQUEST:
   GET http://localhost:5000/broadcasts/nearby?latitude=40.7130&longitude=-74.0059&radius=2&minyanType=mincha

📥 API RESPONSE:
   Status: Success
   Data: [{'id': '...', 'latitude': 40.7128, ...}]

💬 GEMINI FINAL RESPONSE:
   I found 2 nearby mincha minyans within 2 miles...
```

## Architecture

```
User Input
    ↓
Gemini API (with function declarations)
    ↓
Function Call Handler
    ↓
Minyan Finder API (HTTP Request)
    ↓
API Response
    ↓
Function Response to Gemini
    ↓
Gemini Final Response
    ↓
User
```

## Files Overview

- **main.py** - Entry point and interactive CLI
- **gemini_client.py** - Gemini API client with function calling support
- **functions.py** - Function declarations (converted from OpenAPI) and handlers
- **config.py** - Configuration management
- **openapi.yaml** - API specification (source for function declarations)

## Function Declarations

The function declarations are automatically generated from `openapi.yaml`. The system:

1. Parses the OpenAPI specification
2. Extracts relevant operations (createBroadcast, findNearbyBroadcasts)
3. Converts OpenAPI schemas to JSON Schema format
4. Creates Gemini function declarations with proper types and descriptions

## Error Handling

The demo handles various error scenarios:

- **API Connection Errors**: Shows connection failure messages
- **Invalid API Responses**: Displays error details from the API
- **Missing Parameters**: Gemini will ask for clarification
- **Function Call Errors**: Error information is passed back to Gemini

## Troubleshooting

### "GEMINI_API_KEY not found"
- Ensure your `.env` file exists and contains `GEMINI_API_KEY`
- Check that `python-dotenv` is installed

### "Connection refused" or API errors
- Verify the Minyan Finder API is running
- Check `MINYAN_API_BASE_URL` in your `.env` file
- Ensure the API is accessible from your machine

### Function calls not working
- Check that the OpenAPI spec is valid
- Verify function names match between OpenAPI and handlers
- Ensure required parameters are provided in user prompts

## Advanced Usage

### Custom Function Declarations

You can modify `functions.py` to add more functions or customize the declarations. The `convert_openapi_to_gemini_functions()` function can be extended to support additional endpoints.

### Different Gemini Models

Change the model in `.env`:
```env
GEMINI_MODEL=gemini-1.5-pro
```

Available models:
- `gemini-1.5-flash` (faster, recommended for demos)
- `gemini-1.5-pro` (more capable, slower)

## Next Steps

- Add more function calls (updateBroadcast, deleteBroadcast)
- Implement conversation history persistence
- Add multimodal input support (images, etc.)
- Create a web interface instead of CLI

## Support

For issues or questions:
- Check the [Gemini API documentation](https://ai.google.dev/docs)
- Review the OpenAPI specification in `openapi.yaml`
- Check error messages in the console output

