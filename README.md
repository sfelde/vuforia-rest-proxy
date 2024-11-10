# Vuforia Web Services (VWS) API Proxy

This project provides a serverless proxy to interact with Vuforia Web Services (VWS) API using AWS Lambda and API Gateway. It's designed to work with AWS Amplify frontend applications.

## Architecture

- **Frontend**: AWS Amplify JavaScript/React application
- **API Gateway**: Single endpoint `/items` accepting POST requests
- **Lambda**: Python proxy that handles authentication and forwards requests to Vuforia
- **Vuforia**: Target management API

## API Usage

All requests are made as POST to `/items` with different paths and methods in the body.

### CRUD Operations

#### List All Targets

```bash
curl -X POST 'https://your-api-gateway.execute-api.region.amazonaws.com/dev/items' \
-H 'x-api-key: your-api-key' \
-H 'Content-Type: application/json' \
-d '{
    "path": "/targets",
    "http_method": "GET",
    "request_body": ""
}'
```

#### Get Single Target

```bash
curl -X POST 'https://your-api-gateway.execute-api.region.amazonaws.com/dev/items' \
-H 'x-api-key: your-api-key' \
-H 'Content-Type: application/json' \
-d '{
    "path": "/targets/TARGET_ID",
    "http_method": "GET",
    "request_body": ""
}'
```

#### Create Target

```bash
curl -X POST 'https://your-api-gateway.execute-api.region.amazonaws.com/dev/items' \
-H 'x-api-key: your-api-key' \
-H 'Content-Type: application/json' \
-d '{
    "path": "/targets",
    "http_method": "POST",
    "request_body": {
        "name": "test_pattern1",
        "width": 0.2,
        "image": "base64_encoded_image_data"
    }
}'
```

#### Update Target

```bash
curl -X POST 'https://your-api-gateway.execute-api.region.amazonaws.com/dev/items' \
-H 'x-api-key: your-api-key' \
-H 'Content-Type: application/json' \
-d '{
    "path": "/targets/TARGET_ID",
    "http_method": "PUT",
    "request_body": {
        "name": "updated_name",
        "width": 0.3,
        "active_flag": true
    }
}'
```

#### Delete Target

```bash
curl -X POST 'https://your-api-gateway.execute-api.region.amazonaws.com/dev/items' \
-H 'x-api-key: your-api-key' \
-H 'Content-Type: application/json' \
-d '{
    "path": "/targets/TARGET_ID",
    "http_method": "DELETE",
    "request_body": ""
}'
```

## Setup

### Prerequisites

- AWS Account
- Vuforia Developer Account
- Python 3.12+
- AWS CLI
- Amplify CLI

### Configuration

1. Create `config.py`:

```python
VWS_HOSTNAME = 'vws.vuforia.com'
VWS_ACCESS_KEY = 'your_vuforia_access_key'
VWS_SECRET_KEY = 'your_vuforia_secret_key'

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,DELETE',
    'Content-Type': 'application/json'
}
```

2. Deploy Lambda Function
3. Configure API Gateway
4. Set up Amplify frontend

## Documentation Links

- [Vuforia Web Services API](https://library.vuforia.com/web-api/vuforia-web-services-api)
- [AWS Lambda Python](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)
- [API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html)
- [AWS Amplify](https://docs.amplify.aws/)

## Lambda Testing

Test your Lambda function directly in AWS Console:

```json
{
    "path": "/targets",
    "http_method": "GET"
}
```

## Client Implementation

JavaScript/Axios example:

```javascript
axios({
    method: 'post',
    url: '/items',
    data: {
        path: '/targets',
        http_method: 'get',
        request_body: ''
    }
})
```

## Response Format

All responses follow this format:

```json
{
    "statusCode": 200,
    "headers": {
        "Access-Control-Allow-Origin": "*",
        ...
    },
    "body": {
        "status": xxx,
        "response": {
            "result_code": "xxx",
            ...
        }
    }
}
```

## Error Handling

Common Vuforia error codes:

- `TargetStatusNotSuccess`: Target must be in success state before updating
- `AuthenticationFailure`: Invalid credentials
- `RequestTimeTooSkewed`: Time synchronization issue
- `TargetNameExist`: Duplicate target name

## Project Structure

```
├── src/
│   ├── index.py          # Lambda handler
│   └── config.py         # Configuration
│   └── ...
└── README.md
```

## Security

- Use API keys for endpoint protection
- Store Vuforia credentials in AWS Secrets Manager
- Enable CORS only for your domains
- Use IAM roles for Lambda permissions

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
