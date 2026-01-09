from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router import router
from dotenv import load_dotenv

load_dotenv()

"""Main application file for the ChatBot API using FastAPI."""
class ChatBotApi:
    # Constructor
    def __init__(self) -> None:
        self.app = FastAPI( # Calling FastAPI constructor
            title="ChatBot API",
            version="1.0.0",
            docs_url="/chatbot/docs",
            openapi_url="/openapi.json"
        )

        # CORS Middleware configuration, for now it allows all origins for frontend testing
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # with this we allow all origins temporarily
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self.register_routes()

    # Method to register routes (Add the endpoint router to fastapi app)
    def register_routes(self) -> None:
        self.app.include_router(router) # FastAPI method to include a router

# Global instance
chatbot_api = ChatBotApi()
app = chatbot_api.app
