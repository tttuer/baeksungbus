-- init.sql

CREATE DATABASE IF NOT EXISTS test_db;
GRANT ALL PRIVILEGES ON test_db.* TO 'test_user'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;

-- recruit 테이블 생성
CREATE TABLE IF NOT EXISTS recruit (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    department VARCHAR(255) NOT NULL,
    note TEXT
);

-- recruit_experience 테이블 생성
CREATE TABLE IF NOT EXISTS recruit_experience (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recruit_id INT NOT NULL,
    label VARCHAR(255) NOT NULL,
    value TEXT NOT NULL,
    FOREIGN KEY (recruit_id) REFERENCES recruit(id) ON DELETE CASCADE
);

-- 샘플 데이터 삽입
INSERT INTO recruit (title, department, note) VALUES
('승무직', '승무사원', '※ 여객자동차운수사업법에 따라 운수종사자로서 결격사유가 없어야 함\n※ 무경력자는 기능 연수(15일), 현장 연수(15일) 후 채용'),
('정비기술직', '정비기술직', NULL);

INSERT INTO recruit_experience (recruit_id, label, value) VALUES
(1, '경력', '버스 및 대형 화물 경력자'),
(1, '무경력', '1종 대형면허, 버스운전자격증 소지자 중 상기 자격 미해당자'),
(2, '경력', '대형자동차(버스분야) 정비 실무 경력자, 자동차 정비(검사) 관련 유자격자');
