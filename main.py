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
    try:
        body = await request.json()
        user_msg = body['userRequest']['utterance']

        today = datetime.now().strftime("%Y%m%d")

        # 조건: "급식", "밥", "오늘" 중 하나라도 들어가면 오늘 급식 출력
        if any(word in user_msg for word in ["급식", "밥", "오늘"]):
            url = (
                f"https://open.neis.go.kr/hub/mealServiceDietInfo"
                f"?KEY={NEIS_KEY}&Type=json&pIndex=1&pSize=1"
                f"&ATPT_OFCDC_SC_CODE={ATPT_OFCDC_SC_CODE}"
                f"&SD_SCHUL_CODE={SD_SCHUL_CODE}&MLSV_YMD={today}"
            )

            async with httpx.AsyncClient() as client:
                res = await client.get(url, timeout=5.0)
                data = res.json()

                try:
                    meal = data['mealServiceDietInfo'][1]['row'][0]['DDISH_NM']
                    meal = meal.replace("<br/>", "\n").replace(".", "")
                    reply = f"🍽️ 오늘의 급식입니다!\n{meal}"
                except Exception:
                    reply = "오늘의 급식 정보가 없습니다 😥"

        else:
            # 기본값도 그냥 오늘 급식 보여주기 (혼동 없도록)
            url = (
                f"https://open.neis.go.kr/hub/mealServiceDietInfo"
                f"?KEY={NEIS_KEY}&Type=json&pIndex=1&pSize=1"
                f"&ATPT_OFCDC_SC_CODE={ATPT_OFCDC_SC_CODE}"
                f"&SD_SCHUL_CODE={SD_SCHUL_CODE}&MLSV_YMD={today}"
            )
            async with httpx.AsyncClient() as client:
                res = await client.get(url, timeout=5.0)
                data = res.json()

                try:
                    meal = data['mealServiceDietInfo'][1]['row'][0]['DDISH_NM']
                    meal = meal.replace("<br/>", "\n").replace(".", "")
                    reply = f"🍽️ 오늘의 급식입니다!\n{meal}"
                except Exception:
                    reply = "오늘의 급식 정보가 없습니다 😥"

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

    except Exception as e:
        return JSONResponse({
            "version": "2.0",
            "template": {
                "outputs": [{
                    "simpleText": {
                        "text": "서버에서 오류가 발생했습니다 😢"
                    }
                }]
            }
        })
