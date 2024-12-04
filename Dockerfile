# 1. Python 3.12 베이스 이미지 사용
FROM python:3.12-slim

# 2. 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. 작업 디렉토리 생성
WORKDIR /app

# 4. 필요 패키지 설치 (Debian 기반)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 5. Python 의존성 파일 복사
COPY requirements.txt /app/requirements.txt

# 6. Python 라이브러리 설치
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 7. 애플리케이션 소스 코드 복사
COPY . /app

# 8. FastAPI 애플리케이션 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
