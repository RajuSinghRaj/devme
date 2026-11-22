import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(
        host=os.environ.get("DEVTRACK_HOST", "127.0.0.1"),
        port=int(os.environ.get("DEVTRACK_PORT", "5000")),
    )
