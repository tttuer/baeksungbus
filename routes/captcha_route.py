# captcha_routes.py
from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import StreamingResponse
from captcha.image import ImageCaptcha  # captcha 라이브러리 사용
from io import BytesIO
import random
import string
import uuid
import base64

captcha_router = APIRouter()
captcha_store = {}

# CAPTCHA 객체 생성
captcha_generator = ImageCaptcha(width=150, height=50)  # 이미지 크기 조절


# 숫자만 포함된 CAPTCHA 생성
def generate_captcha_text():
    return "".join(random.choices(string.digits, k=5))  # 숫자 5자리로 제한


# CAPTCHA 이미지 생성 엔드포인트
@captcha_router.get("/captcha_image")
async def get_captcha_image():
    global captcha_text
    text = generate_captcha_text()
    captcha_id = str(uuid.uuid4())
    captcha_store[captcha_id] = text

    image = captcha_generator.generate_image(text)
    buffer = BytesIO()
    image.save(buffer, "PNG")
    buffer.seek(0)

    base64_image = base64.b64encode(buffer.read()).decode("utf-8")

    return {
        "captcha_id": captcha_id,
        "image": f"data:image/png;base64,{base64_image}"
    }


# CAPTCHA 확인 및 폼 처리 엔드포인트
@captcha_router.post("/submit")
async def submit_form(captcha_id: str = Form(...), captcha: str = Form(...)):
    expected = captcha_store.get(captcha_id)
    if expected is None or expected != captcha:
        raise HTTPException(status_code=400, detail="Invalid CAPTCHA")
    del captcha_store[captcha_id]
    return {"message": "CAPTCHA verified successfully!"}
