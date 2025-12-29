"""
Function declarations and handlers for Gemini function calling.
Converts OpenAPI spec to Gemini function declarations and handles API calls.
"""
import yaml
import requests
from typing import Dict, Any, List, Optional
from config import MINYAN_API_BASE_URL

# City to coordinates mapping for common US cities
# Format: "City, State" -> (latitude, longitude)
CITY_COORDINATES = {
    # Major cities
    'New York, NY': (40.7128, -74.0060),
    'Los Angeles, CA': (34.0522, -118.2437),
    'Chicago, IL': (41.8781, -87.6298),
    'Houston, TX': (29.7604, -95.3698),
    'Phoenix, AZ': (33.4484, -112.0740),
    'Philadelphia, PA': (39.9526, -75.1652),
    'San Antonio, TX': (29.4241, -98.4936),
    'San Diego, CA': (32.7157, -117.1611),
    'Dallas, TX': (32.7767, -96.7970),
    'San Jose, CA': (37.3382, -121.8863),
    'Austin, TX': (30.2672, -97.7431),
    'Jacksonville, FL': (30.3322, -81.6557),
    'Fort Worth, TX': (32.7555, -97.3308),
    'Columbus, OH': (39.9612, -82.9988),
    'Charlotte, NC': (35.2271, -80.8431),
    'San Francisco, CA': (37.7749, -122.4194),
    'Indianapolis, IN': (39.7684, -86.1581),
    'Seattle, WA': (47.6062, -122.3321),
    'Denver, CO': (39.7392, -104.9903),
    'Washington, DC': (38.9072, -77.0369),
    'Boston, MA': (42.3601, -71.0589),
    'El Paso, TX': (31.7619, -106.4850),
    'Detroit, MI': (42.3314, -83.0458),
    'Nashville, TN': (36.1627, -86.7816),
    'Portland, OR': (45.5152, -122.6784),
    'Oklahoma City, OK': (35.4676, -97.5164),
    'Las Vegas, NV': (36.1699, -115.1398),
    'Memphis, TN': (35.1495, -90.0490),
    'Louisville, KY': (38.2527, -85.7585),
    'Baltimore, MD': (39.2904, -76.6122),
    'Milwaukee, WI': (43.0389, -87.9065),
    'Albuquerque, NM': (35.0844, -106.6504),
    'Tucson, AZ': (32.2226, -110.9747),
    'Fresno, CA': (36.7378, -119.7871),
    'Sacramento, CA': (38.5816, -121.4944),
    'Kansas City, MO': (39.0997, -94.5786),
    'Mesa, AZ': (33.4152, -111.8315),
    'Atlanta, GA': (33.7490, -84.3880),
    'Omaha, NE': (41.2565, -95.9345),
    'Colorado Springs, CO': (38.8339, -104.8214),
    'Raleigh, NC': (35.7796, -78.6382),
    'Virginia Beach, VA': (36.8529, -75.9780),
    'Miami, FL': (25.7617, -80.1918),
    'Oakland, CA': (37.8044, -122.2712),
    'Minneapolis, MN': (44.9778, -93.2650),
    'Tulsa, OK': (36.1540, -95.9928),
    'Cleveland, OH': (41.4993, -81.6944),
    'Wichita, KS': (37.6872, -97.3301),
    'Arlington, TX': (32.7357, -97.1081),
    'New Orleans, LA': (29.9511, -90.0715),
    'Tampa, FL': (27.9506, -82.4572),
    'Honolulu, HI': (21.3099, -157.8581),
    
    # NYC Boroughs and neighborhoods
    'Manhattan, NY': (40.7831, -73.9712),
    'Brooklyn, NY': (40.6782, -73.9442),
    'Queens, NY': (40.7282, -73.7949),
    'Bronx, NY': (40.8448, -73.8648),
    'Staten Island, NY': (40.5795, -74.1502),
    'Upper West Side, NY': (40.7870, -73.9754),
    'Upper East Side, NY': (40.7736, -73.9566),
    'Midtown, NY': (40.7549, -73.9840),
    'Lower Manhattan, NY': (40.7074, -74.0113),
    'Harlem, NY': (40.8176, -73.9482),
    'East Village, NY': (40.7265, -73.9815),
    'West Village, NY': (40.7358, -74.0036),
    'SoHo, NY': (40.7231, -74.0026),
    'Tribeca, NY': (40.7163, -74.0086),
    'Chinatown, NY': (40.7158, -73.9970),
    'Little Italy, NY': (40.7191, -73.9973),
    'Greenwich Village, NY': (40.7336, -74.0027),
    'Chelsea, NY': (40.7465, -74.0014),
    'Park Slope, Brooklyn, NY': (40.6712, -73.9858),
    'Williamsburg, Brooklyn, NY': (40.7081, -73.9571),
    'Astoria, Queens, NY': (40.7700, -73.9308),
    'Flushing, Queens, NY': (40.7654, -73.8300),
    'Jamaica, Queens, NY': (40.7021, -73.8019),
    'Long Island City, Queens, NY': (40.7447, -73.9485),
    
    # Long Island cities
    'Cedarhurst, NY': (40.6218, -73.7246),
    'Lawrence, NY': (40.6157, -73.7296),
    'Woodmere, NY': (40.6320, -73.7146),
    'Inwood, NY': (40.6220, -73.7468),
    'Far Rockaway, NY': (40.6054, -73.7557),
    'Five Towns, NY': (40.6218, -73.7246),  # Approximate center
    'Great Neck, NY': (40.7873, -73.7262),
    'Roslyn, NY': (40.8007, -73.6504),
    'Port Washington, NY': (40.8257, -73.6982),
    'Garden City, NY': (40.7268, -73.6343),
    'Rockville Centre, NY': (40.6587, -73.6412),
    'Lynbrook, NY': (40.6548, -73.6718),
    'Valley Stream, NY': (40.6643, -73.7085),
    'Oceanside, NY': (40.6384, -73.6401),
    'Baldwin, NY': (40.6565, -73.6093),
    'Merrick, NY': (40.6629, -73.5515),
    'Bellmore, NY': (40.6687, -73.5271),
    'Wantagh, NY': (40.6743, -73.5101),
    'Seaford, NY': (40.6659, -73.5022),
    'Massapequa, NY': (40.6807, -73.4743),
    'Amityville, NY': (40.6789, -73.4171),
    'Lindenhurst, NY': (40.6868, -73.3735),
    'West Babylon, NY': (40.7432, -73.3537),
    'Deer Park, NY': (40.7618, -73.3293),
    'Commack, NY': (40.8429, -73.2929),
    'Huntington Station, NY': (40.8534, -73.4115),
    'Dix Hills, NY': (40.8048, -73.3362),
    'Plainview, NY': (40.7765, -73.4673),
    'Syosset, NY': (40.8262, -73.5021),
    'Hicksville, NY': (40.7684, -73.5251),
    'Levittown, NY': (40.7259, -73.5143),
    'Bethpage, NY': (40.7443, -73.4821),
    'Farmingdale, NY': (40.7326, -73.4454),
    'East Meadow, NY': (40.7140, -73.5590),
    'Uniondale, NY': (40.7004, -73.5929),
    'Hempstead, NY': (40.7062, -73.6187),
    'Freeport, NY': (40.6576, -73.5832),
    'Long Beach, NY': (40.5884, -73.6580),
    
    # Other major cities
    'Buffalo, NY': (42.8864, -78.8784),
    'Rochester, NY': (43.1566, -77.6088),
    'Yonkers, NY': (40.9312, -73.8988),
    'Syracuse, NY': (43.0481, -76.1474),
    'Albany, NY': (42.6526, -73.7562),
    'New Rochelle, NY': (40.9115, -73.7824),
    'Mount Vernon, NY': (40.9126, -73.8371),
    'Schenectady, NY': (42.8142, -73.9396),
    'Utica, NY': (43.1009, -75.2327),
    'White Plains, NY': (41.0340, -73.7629),
    'Troy, NY': (42.7284, -73.6918),
    'Niagara Falls, NY': (43.0962, -79.0377),
    'Binghamton, NY': (42.0987, -75.9180),
    'Rome, NY': (43.2128, -75.4557),
    'Ithaca, NY': (42.4434, -76.5016),
    'Poughkeepsie, NY': (41.7004, -73.9210),
    'Jamestown, NY': (42.0970, -79.2353),
    'Elmira, NY': (42.0898, -76.8077),
    'Watertown, NY': (43.9748, -75.9108),
    'Auburn, NY': (42.9334, -76.5666),
    'Glen Cove, NY': (40.8623, -73.6337),
    'Plattsburgh, NY': (44.6995, -73.4529),
    'Batavia, NY': (43.0006, -78.1923),
    'Oswego, NY': (43.4565, -76.5105),
    'Kingston, NY': (41.9270, -74.0000),
    'Middletown, NY': (41.4459, -74.4229),
    'Oneonta, NY': (42.4529, -75.0638),
    'Cortland, NY': (42.6012, -76.1805),
    'Glens Falls, NY': (43.3095, -73.6440),
    'Lockport, NY': (43.1706, -78.6903),
}


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
    First checks local city coordinates map, then falls back to Nominatim API.
    """
    location = args.get('location', '').strip()
    if not location:
        return {
            'success': False,
            'error': 'Location parameter is required'
        }
    
    # Normalize location string for lookup (case-insensitive)
    location_normalized = location
    
    # Try exact match first
    if location_normalized in CITY_COORDINATES:
        lat, lon = CITY_COORDINATES[location_normalized]
        return {
            'success': True,
            'data': {
                'location': location,
                'latitude': lat,
                'longitude': lon,
                'display_name': location,
                'source': 'local_map'
            }
        }
    
    # Try case-insensitive lookup
    location_lower = location_normalized.lower()
    for city, coords in CITY_COORDINATES.items():
        if city.lower() == location_lower:
            lat, lon = coords
            return {
                'success': True,
                'data': {
                    'location': location,
                    'latitude': lat,
                    'longitude': lon,
                    'display_name': city,
                    'source': 'local_map'
                }
            }
    
    # Try partial match (e.g., "Manhattan" matches "Manhattan, NY")
    for city, coords in CITY_COORDINATES.items():
        city_name = city.split(',')[0].strip().lower()
        if location_lower == city_name or location_lower in city.lower() or city.lower() in location_lower:
            lat, lon = coords
            return {
                'success': True,
                'data': {
                    'location': location,
                    'latitude': lat,
                    'longitude': lon,
                    'display_name': city,
                    'source': 'local_map'
                }
            }
    
    # Fall back to Nominatim API if not found in local map
    try:
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
                'display_name': result.get('display_name', location),
                'source': 'nominatim_api'
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
    
    # Note: geocodeLocation function removed - coordinates are now included directly in user messages
    # The handle_geocode_location function is kept as a backend utility but not exposed to Gemini
    
    return functions

