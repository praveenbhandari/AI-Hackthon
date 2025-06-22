# CORS Configuration Fix

## Problem
The frontend running on `http://localhost:3000` was unable to access the FastAPI backend running on `http://localhost:8000` due to CORS (Cross-Origin Resource Sharing) policy restrictions.

Error messages:
```
Access to XMLHttpRequest at 'http://localhost:8000/health' from origin 'http://localhost:3000' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

## Solution
Added CORS middleware to all FastAPI applications to allow cross-origin requests from the frontend.

### Files Modified

1. **`src/bc/api.py`** (Port 8000)
   - Added `from fastapi.middleware.cors import CORSMiddleware`
   - Added CORS middleware configuration

2. **`src/bc/crew_fastapi.py`** (Port 8002)
   - Added `from fastapi.middleware.cors import CORSMiddleware`
   - Added CORS middleware configuration

3. **`src/bc/agents.py`** (Port 8001)
   - Added `from fastapi.middleware.cors import CORSMiddleware`
   - Added CORS middleware configuration
   - Fixed port conflict by changing from 8000 to 8001

### CORS Configuration
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)
```

## Port Configuration
- **Main API**: `http://localhost:8000` (src/bc/api.py)
- **Agents API**: `http://localhost:8001` (src/bc/agents.py)
- **Crew API**: `http://localhost:8002` (src/bc/crew_fastapi.py)

## Testing
Run the CORS test script to verify the configuration:
```bash
python test_cors.py
```

## Next Steps
1. Restart your FastAPI server(s)
2. The frontend should now be able to make requests to the backend without CORS errors
3. If you're still experiencing issues, check that the correct API server is running on the expected port

## Additional Notes
- The CORS configuration allows requests from both `localhost:3000` and `127.0.0.1:3000`
- All HTTP methods and headers are allowed for maximum flexibility
- Credentials are allowed for authenticated requests if needed 