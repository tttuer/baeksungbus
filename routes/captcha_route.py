# captcha_routes.py
from fastapi import APIRouter, Form, HTTPException
from captcha.image import ImageCaptcha  # captcha 라이브러리 사용
from io import BytesIO
import random
import string
import uuid
import base64
import logging
import secrets
import time

captcha_router = APIRouter()
captcha_store = {}
CAPTCHA_TTL_SECONDS = 300
CAPTCHA_MAX_ATTEMPTS = 5

# CAPTCHA 객체 생성
captcha_generator = ImageCaptcha(width=150, height=50)  # 이미지 크기 조절


# 숫자만 포함된 CAPTCHA 생성
def generate_captcha_text():
    return "".join(random.choices(string.digits, k=5))  # 숫자 5자리로 제한


def cleanup_expired_captchas(now: float | None = None):
    now = now or time.time()
    expired_ids = [
        captcha_id
        for captcha_id, challenge in captcha_store.items()
        if challenge["expires_at"] <= now
    ]
    for captcha_id in expired_ids:
        captcha_store.pop(captcha_id, None)


def verify_and_consume_captcha(captcha_id: str, captcha: str):
    cleanup_expired_captchas()

    challenge = captcha_store.get(captcha_id)
    if not challenge:
        logging.warning("Invalid or expired CAPTCHA id=%s", captcha_id)
        raise HTTPException(status_code=400, detail="Invalid CAPTCHA")

    if challenge["attempts"] >= CAPTCHA_MAX_ATTEMPTS:
        captcha_store.pop(captcha_id, None)
        logging.warning("CAPTCHA attempts exceeded id=%s", captcha_id)
        raise HTTPException(status_code=400, detail="Invalid CAPTCHA")

    challenge["attempts"] += 1
    if not secrets.compare_digest(challenge["answer"], captcha.strip()):
        logging.warning("Invalid CAPTCHA value id=%s", captcha_id)
        raise HTTPException(status_code=400, detail="Invalid CAPTCHA")

    captcha_store.pop(captcha_id, None)


# CAPTCHA 이미지 생성 엔드포인트
@captcha_router.get("/captcha_image")
async def get_captcha_image():
    cleanup_expired_captchas()

    text = generate_captcha_text()
    captcha_id = str(uuid.uuid4())
    now = time.time()
    captcha_store[captcha_id] = {
        "answer": text,
        "created_at": now,
        "expires_at": now + CAPTCHA_TTL_SECONDS,
        "attempts": 0,
    }

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
    verify_and_consume_captcha(captcha_id, captcha)
    return {"message": "CAPTCHA verified successfully!"}
