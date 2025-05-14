from fastapi.middleware.cors import CORSMiddleware

class CORSCustomMiddleware(CORSMiddleware):
    def __init__(self, app):
        origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000"
        ]

        super().__init__(
            app,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )