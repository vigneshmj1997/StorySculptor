from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import traceback
from app.api.reel import Reel

app = FastAPI()


class RequestModel(BaseModel):
    story: str


@app.post("/synthesize")
def synthesize(request: RequestModel, background: BackgroundTasks):
    try:
        make_reel = Reel(request.story)
        make_reel.make_reel()
    except Exception as exc:
        tb_str = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        print(tb_str)
        raise HTTPException(status_code=200, detail=f"{exc}")
