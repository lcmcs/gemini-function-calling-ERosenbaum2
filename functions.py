"""
Function declarations and handlers for Gemini function calling.
Converts OpenAPI spec to Gemini function declarations and handles API calls.
"""
import yaml
import requests
from typing import Dict, Any, List
from config import MINYAN_API_BASE_URL


def load_openapi_spec(file_path: str = 'openapi.yaml') -> Dict[str, Any]:
    """Load and parse the OpenAPI specification file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def convert_openapi_to_gemini_functions(openapi_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Convert OpenAPI operations to Gemini function declarations.
    Focuses on createBroadcast and findNearbyBroadcasts as required.
    """
    functions = []
    paths = openapi_spec.get('paths', {})
    components = openapi_spec.get('components', {}).get('schemas', {})
    
    # Helper function to convert OpenAPI schema to JSON schema
    def convert_schema(schema_ref: str) -> Dict[str, Any]:
        """Convert OpenAPI schema reference to JSON schema."""
        if schema_ref.startswith('#/components/schemas/'):
            schema_name = schema_ref.split('/')[-1]
            schema = components.get(schema_name, {})
            return convert_openapi_schema_to_json(schema)
        return {}
    
    def convert_openapi_schema_to_json(schema: Dict[str, Any]) -> Dict[str, Any]:
        """Convert OpenAPI schema to JSON schema format."""
        json_schema = {
            'type': schema.get('type', 'object'),
            'properties': {},
            'required': schema.get('required', [])
        }
        
        if 'properties' in schema:
            for prop_name, prop_schema in schema['properties'].items():
                prop_json = {
                    'type': prop_schema.get('type', 'string'),
                    'description': prop_schema.get('description', '')
                }
                
                # Add format if present
                if 'format' in prop_schema:
                    prop_json['format'] = prop_schema['format']
                
                # Add enum if present
                if 'enum' in prop_schema:
                    prop_json['enum'] = prop_schema['enum']
                
                # Note: Gemini function calling API doesn't support minimum/maximum constraints
                # Add constraint info to description if present
                if 'minimum' in prop_schema or 'maximum' in prop_schema:
                    constraints = []
                    if 'minimum' in prop_schema:
                        constraints.append(f"minimum: {prop_schema['minimum']}")
                    if 'maximum' in prop_schema:
                        constraints.append(f"maximum: {prop_schema['maximum']}")
                    if constraints:
                        prop_json['description'] = (prop_json.get('description', '') + 
                                                    f" (Constraints: {', '.join(constraints)})").strip()
                
                json_schema['properties'][prop_name] = prop_json
        
        return json_schema
    
    # Function 1: createBroadcast
    if '/broadcasts' in paths and 'post' in paths['/broadcasts']:
        post_op = paths['/broadcasts']['post']
        request_schema_ref = post_op.get('requestBody', {}).get('content', {}).get('application/json', {}).get('schema', {}).get('$ref', '')
        
        if request_schema_ref:
            request_schema = convert_schema(request_schema_ref)
            functions.append({
                'name': 'createBroadcast',
                'description': post_op.get('description', 'Create a new broadcast when looking for a minyan.'),
                'parameters': request_schema
            })
    
    # Function 2: findNearbyBroadcasts
    if '/broadcasts/nearby' in paths and 'get' in paths['/broadcasts/nearby']:
        get_op = paths['/broadcasts/nearby']['get']
        parameters = get_op.get('parameters', [])
        
        # Convert parameters to JSON schema
        properties = {}
        required = []
        
        for param in parameters:
            param_name = param.get('name')
            param_schema = param.get('schema', {})
            
            prop = {
                'type': param_schema.get('type', 'string'),
                'description': param.get('description', '')
            }
            
            if 'format' in param_schema:
                prop['format'] = param_schema['format']
            if 'enum' in param_schema:
                prop['enum'] = param_schema['enum']
            
            # Note: Gemini function calling API doesn't support minimum/maximum constraints
            # Add constraint info to description if present
            if 'minimum' in param_schema or 'maximum' in param_schema:
                constraints = []
                if 'minimum' in param_schema:
                    constraints.append(f"minimum: {param_schema['minimum']}")
                if 'maximum' in param_schema:
                    constraints.append(f"maximum: {param_schema['maximum']}")
                if constraints:
                    prop['description'] = (prop.get('description', '') + 
                                          f" (Constraints: {', '.join(constraints)})").strip()
            
            properties[param_name] = prop
            
            if param.get('required', False):
                required.append(param_name)
        
        functions.append({
            'name': 'findNearbyBroadcasts',
            'description': get_op.get('description', 'Find people near you who need the same minyan.'),
            'parameters': {
                'type': 'object',
                'properties': properties,
                'required': required
            }
        })
    
    return functions


def handle_create_broadcast(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle the createBroadcast function call.
    Makes a POST request to /broadcasts endpoint.
    """
    url = f"{MINYAN_API_BASE_URL}/broadcasts"
    
    try:
        response = requests.post(url, json=args, timeout=10)
        response.raise_for_status()
        return {
            'success': True,
            'data': response.json()
        }
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': str(e),
            'status_code': getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None,
            'response_text': getattr(e.response, 'text', None) if hasattr(e, 'response') else None
        }


def handle_find_nearby_broadcasts(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle the findNearbyBroadcasts function call.
    Makes a GET request to /broadcasts/nearby endpoint.
    """
    url = f"{MINYAN_API_BASE_URL}/broadcasts/nearby"
    
    try:
        response = requests.get(url, params=args, timeout=10)
        response.raise_for_status()
        return {
            'success': True,
            'data': response.json()
        }
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': str(e),
            'status_code': getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None,
            'response_text': getattr(e.response, 'text', None) if hasattr(e, 'response') else None
        }


def handle_geocode_location(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle geocoding a location name to coordinates.
    Uses Nominatim (OpenStreetMap) free geocoding service.
    """
    location = args.get('location', '').strip()
    if not location:
        return {
            'success': False,
            'error': 'Location parameter is required'
        }
    
    try:
        # Use Nominatim (OpenStreetMap) free geocoding API
        url = 'https://nominatim.openstreetmap.org/search'
        params = {
            'q': location,
            'format': 'json',
            'limit': 1
        }
        headers = {
            'User-Agent': 'MinyanFinder/1.0'  # Required by Nominatim
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        results = response.json()
        if not results:
            return {
                'success': False,
                'error': f'Location "{location}" not found'
            }
        
        result = results[0]
        return {
            'success': True,
            'data': {
                'location': location,
                'latitude': float(result['lat']),
                'longitude': float(result['lon']),
                'display_name': result.get('display_name', location)
            }
        }
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f'Geocoding failed: {str(e)}'
        }
    except (KeyError, ValueError) as e:
        return {
            'success': False,
            'error': f'Invalid geocoding response: {str(e)}'
        }


def execute_function(function_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a function call by name.
    Routes to the appropriate handler.
    """
    handlers = {
        'createBroadcast': handle_create_broadcast,
        'findNearbyBroadcasts': handle_find_nearby_broadcasts,
        'geocodeLocation': handle_geocode_location
    }
    
    handler = handlers.get(function_name)
    if not handler:
        return {
            'success': False,
            'error': f'Unknown function: {function_name}'
        }
    
    return handler(args)


def get_gemini_functions() -> List[Dict[str, Any]]:
    """
    Get Gemini function declarations from OpenAPI spec.
    Main entry point for getting functions.
    """
    openapi_spec = load_openapi_spec()
    functions = convert_openapi_to_gemini_functions(openapi_spec)
    
    # Add geocoding function (not in OpenAPI spec)
    functions.append({
        'name': 'geocodeLocation',
        'description': 'Convert a location name (city, neighborhood, address) to latitude and longitude coordinates. Use this when the user provides a location name instead of coordinates.',
        'parameters': {
            'type': 'object',
            'properties': {
                'location': {
                    'type': 'string',
                    'description': 'Location name (e.g., "Cedarhurst NY", "Manhattan", "Upper West Side, New York")'
                }
            },
            'required': ['location']
        }
    })
    
    return functions

