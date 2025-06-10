from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
from datetime import datetime
import os

app = FastAPI()

# NEIS API 키와 학교 정보
NEIS_KEY = "e31fe025c01a43049d9621f0922895f2" #api
ATPT_OFCDC_SC_CODE = "B10"  #서울교육청
SD_SCHUL_CODE = "7011109"   #사대부고 번호

@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    user_msg = body['userRequest']['utterance']

    # 날짜 계산 (오늘 급식)
    today = datetime.now().strftime("%Y%m%d")

    # 조건 확인
    if "오늘 급식" in user_msg or "오늘 밥" in user_msg:
        # NEIS 급식 API 호출
        url = (
            f"https://open.neis.go.kr/hub/mealServiceDietInfo"
            f"?KEY={NEIS_KEY}&Type=json&pIndex=1&pSize=1"
            f"&ATPT_OFCDC_SC_CODE={ATPT_OFCDC_SC_CODE}"
            f"&SD_SCHUL_CODE={SD_SCHUL_CODE}&MLSV_YMD={today}"
        )

        async with httpx.AsyncClient() as client:
            try:
                res = await client.get(url, timeout=5.0)
                data = res.json()

                meal = data['mealServiceDietInfo'][1]['row'][0]['DDISH_NM']
                meal = meal.replace("<br/>", "\n").replace(".", "")

                reply = f"🍽️ 오늘의 급식입니다!\n{meal}"

            except Exception:
                reply = "오늘의 급식 정보를 불러오지 못했어요. 😥"
    else:
        reply = "무슨 급식이 궁금한가요? '오늘 급식 알려줘'처럼 말해보세요!"

    # 카카오톡 응답 포맷
    return JSONResponse({
        "version": "2.0",
        "template": {
            "outputs": [{
                "simpleText": {
                    "text": reply
                }
            }]
        }
    })
