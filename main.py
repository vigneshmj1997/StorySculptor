from dotenv import load_dotenv

load_dotenv(".env")
import uvicorn
from app.api.main import app

uvicorn.run(app)
