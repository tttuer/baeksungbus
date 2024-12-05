// ddocks 데이터를 서버에서 가져오는 함수
async function fetchDdocks() {
    try {
        const response = await fetch('/api/ddocks'); // FastAPI 엔드포인트
        if (!response.ok) {
            throw new Error('Failed to fetch ddocks');
        }

        const data = await response.json();
        renderDdocks(data.ddocks);
    } catch (error) {
        console.error('Error:', error);
    }
}

// ddocks 데이터를 #editor에 렌더링하는 함수
function renderDdocks(ddocks) {
    const editor = document.getElementById('editor');
    editor.innerHTML = ''; // 기존 내용을 초기화

    ddocks.forEach(ddock => {
        if (ddock.image) {
            const img = document.createElement('img');
            img.src = `data:image/png;base64,${ddock.image}`;
            img.alt = 'Image';
            img.style = 'max-width: 100%; margin-bottom: 10px;'; // 이미지 스타일 설정
            editor.appendChild(img);
        }
    });
}

// 페이지 로드 시 ddocks 데이터를 가져옴
document.addEventListener('DOMContentLoaded', fetchDdocks);
