## 백엔드 Docker 실행 방법

이 프로젝트의 `docker-compose.yml`은 MySQL DB만 실행합니다. 백엔드 앱은
`Dockerfile`로 이미지를 빌드한 뒤 별도로 실행합니다.

### 1. DB 실행

```bash
docker compose up -d
```

### 2. 기존 데이터 삭제 후 DB 다시 실행

기존 MySQL 데이터까지 모두 삭제하고 새로 시작하려면 아래 명령을 사용합니다.

```bash
docker compose down -v
docker compose up -d
```

`down -v`는 Docker volume을 삭제하므로 기존 DB 데이터가 모두 사라집니다.

### 3. Alembic 마이그레이션 실행

DB를 실행한 뒤 테이블을 생성하거나 최신 스키마로 업데이트합니다.

```bash
uv run alembic upgrade head
```

이미 적용된 마이그레이션은 `alembic_version` 테이블에 기록되므로, 같은 명령을
다시 실행해도 기존 테이블을 다시 만들거나 덮어쓰지 않습니다.

모델을 수정한 뒤 새 마이그레이션을 만들 때는 다음 명령을 사용합니다.

```bash
uv run alembic revision --autogenerate -m "변경 내용 설명"
uv run alembic upgrade head


```text
http://localhost:8000
```

### 전체 초기화 후 실행 예시

기존 DB 데이터를 삭제하고, DB를 다시 올린 뒤, 마이그레이션을 적용하고,
백엔드를 실행하는 전체 예시는 다음과 같습니다.

```bash
docker compose down -v
docker compose up -d
uv run alembic upgrade head
```
