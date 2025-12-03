# FastApi + MongoDb + Selenium + BeautifulSoup + polars for css analitics

from fastapi import FastAPI
# from app.db import db
# from app.selenium_worker import submit_task

app = FastAPI()

@app.get("/")
async def root():
    return {
        "message": "Health",
        "statusCode": 200
        }








if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
    # uvicorn app.main:app --reload