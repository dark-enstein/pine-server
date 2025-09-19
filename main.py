# 1. Import required modules
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from model.model import echo

# 2. Define a Pydantic model for request body validation
# This ensures that any POST request to our endpoint MUST have a 'name' field that is a string.
class UserRequest(BaseModel):
    name: str

# 3. Create an instance of the FastAPI app
app = FastAPI()

# 4. Configure CORS (Cross-Origin Resource Sharing)
# This allows your Vue.js frontend (e.g., running on http://localhost:5173) 
# to communicate with this backend.
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def process_user():
    call = echo()
    return {"message": f"{call}"}

# 5. Define the API endpoint
@app.post("/api/user")
async def process_user(user_request: UserRequest):
    # FastAPI automatically validates the incoming request against the UserRequest model.
    # If the 'name' field is missing or not a string, it will automatically return a 422 error.
    
    name = user_request.name
    print(f"Received name: {name}")

    # Create a new string as the output
    response_message = f"Hello from Python, {name}! Your request was received at {datetime.now().strftime('%-I:%M:%S %p')}."

    # Return a dictionary, which FastAPI automatically converts to a JSON response
    return {"message": response_message}
