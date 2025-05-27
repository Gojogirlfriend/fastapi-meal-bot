from fastapi import FastAPI, Request
import httpx

app = FastAPI()

@app.post("/webhook")
async def kakao_webhook(request: Request):
    req_json = await request.json()

    # 예: 서울시교육청 휘문고 2024년 5월 27일
    office_code = "B10"  # 서울시교육청
    school_code = "7010569"  # 휘문고등학교
    date = "20240527"  # 오늘 날짜 형식 YYYYMMDD

    api_key = "e31fe025c01a43049d9621f0922895f2"  # https://open.neis.go.kr에서 발급받기

    url = (
        f"https://open.neis.go.kr/hub/mealServiceDietInfo"
        f"?KEY={api_key}&Type=json&ATPT_OFCDC_SC_CODE={office_code}"
        f"&SD_SCHUL_CODE={school_code}&MLSV_YMD={date}"
    )

    async with httpx.AsyncClient() as client:
        res = await client.get(url)
        data = res.json()

    try:
        meal_info = data['mealServiceDietInfo'][1]['row'][0]['DDISH_NM']
    except:
        meal_info = "급식 정보가 없습니다."

    return {
        "version": "2.0",
        "template": {
            "outputs": [{
                "simpleText": {
                    "text": f"오늘의 급식은:\n{meal_info.replace('<br/>', '\n')}"
                }
            }]
        }
    }
