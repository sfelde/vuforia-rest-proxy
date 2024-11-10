import json
import hashlib
import hmac
import base64
from datetime import datetime
import urllib3
from typing import Dict, Any
from config import VWS_HOSTNAME, VWS_ACCESS_KEY, VWS_SECRET_KEY, CORS_HEADERS

def compute_signature(secret_key: str, string_to_sign: str) -> str:
    key_bytes = secret_key.encode('utf-8')
    data_bytes = string_to_sign.encode('utf-8')
    
    h = hmac.new(key_bytes, None, hashlib.sha1)
    h.update(data_bytes)
    return base64.b64encode(h.digest()).decode('utf-8')

def get_authorization_header(access_key: str, secret_key: str, method: str, 
                           content: str, content_type: str, date: str, 
                           request_path: str) -> str:
    components = [
        method,
        hashlib.md5(content.encode('utf-8')).hexdigest(),
        content_type,
        date,
        request_path
    ]
    string_to_sign = '\n'.join(components)
    signature = compute_signature(secret_key, string_to_sign)
    return f"VWS {access_key}:{signature}"

def make_vuforia_request(method: str, path: str, body: str = '') -> Dict[str, Any]:
    http = urllib3.PoolManager()
    
    content_type = 'application/json'
    date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    if not path.startswith('/'):
        path = '/' + path
        
    headers = {
        'Authorization': get_authorization_header(
            VWS_ACCESS_KEY, VWS_SECRET_KEY, method, body, content_type, date, path
        ),
        'Content-Type': content_type,
        'Date': date
    }
    
    url = f'https://{VWS_HOSTNAME}{path}'
    print(f"Making request to: {url}")
    print(f"Request body: \n{body}")
    
    try:
        response = http.request(
            method,
            url,
            headers=headers,
            body=body.encode('utf-8') if body else None
        )
        
        response_data = response.data.decode('utf-8')
        print(f"Vuforia response: \n{response_data}")
        
        try:
            parsed_response = json.loads(response_data)
            return {
                'status': 403 if parsed_response.get('result_code') == 'TargetStatusNotSuccess' else response.status,
                'response': parsed_response
            }
        except json.JSONDecodeError:
            return {
                'status': response.status,
                'response': response_data
            }
        
    except Exception as e:
        return {
            'status': 500,
            'response': {
                'result_code': 'Fail',
                'error': str(e)
            }
        }

def process_request(method: str, path: str, request_body: Any = None) -> Dict[str, Any]:
    """Process Vuforia API request - direct passthrough for updates"""
    try:
        # For PUT/UPDATE requests - direct passthrough
        if method == 'PUT' and path.startswith('/targets/'):
            # Convert None values and prepare request body
            if isinstance(request_body, dict):
                # Remove None values
                request_body = {k: v for k, v in request_body.items() if v is not None}
                
                # Convert width to float if present
                if 'width' in request_body:
                    request_body['width'] = float(request_body['width'])
                
                body = json.dumps(request_body)
            else:
                body = ''
                
            # Direct passthrough to Vuforia
            return make_vuforia_request(method, path, body)

        # Other requests remain unchanged
        elif method == 'POST' and path == '/targets':
            return make_vuforia_request('POST', '/targets', json.dumps(request_body))
        elif method == 'GET' and path == '/targets':
            return make_vuforia_request('GET', '/targets')
        elif method == 'DELETE' and path.startswith('/targets/'):
            target_id = path.split('/targets/')[1]
            return make_vuforia_request('DELETE', f'/targets/{target_id}')
        elif method == 'GET' and path.startswith('/targets/'):
            target_id = path.split('/targets/')[1]
            return make_vuforia_request('GET', f'/targets/{target_id}')
        else:
            if isinstance(request_body, dict):
                request_body = json.dumps(request_body)
            return make_vuforia_request(method, path, request_body or '')
            
    except Exception as e:
        print(f"Process request error: {str(e)}")
        return {
            'status': 500,
            'response': {
                'result_code': 'Fail',
                'error': str(e)
            }
        }

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    print("\n=== LAMBDA HANDLER START ===")
    print("Event:", json.dumps(event))
    
    try:
        # Parse request parameters
        body = event.get('body', event)  # Use event directly for Lambda tests
        if isinstance(body, str):
            body = json.loads(body)
        
        http_method = body.get('http_method', '').upper()
        path = body.get('path', '')
        request_body = body.get('request_body', {})
        
        print(f"Processed request - Method: {http_method}, Path: {path}")
        print(f"Request body: {json.dumps(request_body)}")
        
        # Process request
        result = process_request(http_method, path, request_body)
        
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps(result)
        }
        
    except Exception as e:
        print(f"Handler error: {str(e)}")
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'status': 500,
                'response': {
                    'result_code': 'Fail',
                    'error': str(e)
                }
            })
        }