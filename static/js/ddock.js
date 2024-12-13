// ddocks 데이터를 서버에서 가져오는 함수
async function fetchDdocks() {
    const editor = document.getElementById('editor');

    // 로딩 스피너 추가
    const spinner = document.createElement('div');
    spinner.className = 'spinner-border';
    spinner.role = 'status';
    spinner.innerHTML = '<span class="visually-hidden">Loading...</span>';
    editor.appendChild(spinner);

    try {
        const response = await fetch('/api/ddocks'); // FastAPI 엔드포인트
        if (!response.ok) {
            throw new Error('Failed to fetch ddocks');
        }

        const data = await response.json();

        // 데이터를 렌더링 (이미지를 하나씩 순차적으로 보여줌)
        await renderDdocksSequentially(data.ddocks);

    } catch (error) {
        console.error('Error:', error);
        editor.innerHTML = '<p>Failed to load data.</p>'; // 로딩 실패 메시지 표시
    } finally {
        // 로딩 스피너 제거 (모든 작업이 완료된 후 제거)
        spinner.remove();
    }
}

// ddocks 데이터를 순차적으로 렌더링하는 함수
async function renderDdocksSequentially(ddocks) {
    const editor = document.getElementById('editor');
    editor.innerHTML = ''; // 기존 내용을 초기화

    for (const ddock of ddocks) {
        if (ddock.image) {
            const img = document.createElement('img');
            img.src = `data:image/png;base64,${ddock.image}`;
            img.alt = 'Image';
            img.style = 'max-width: 100%; margin-bottom: 10px;'; // 이미지 스타일 설정

            // 이미지가 로드될 때까지 대기
            await new Promise((resolve) => {
                img.onload = () => resolve();
            });

            // 이미지를 DOM에 추가
            editor.appendChild(img);

            // 약간의 지연 시간을 추가하여 더 자연스럽게 보이도록 설정 (선택 사항)
            await new Promise((resolve) => setTimeout(resolve, 200)); // 200ms 지연
        }
    }
}

// 페이지 로드 시 ddocks 데이터를 가져옴
document.addEventListener('DOMContentLoaded', fetchDdocks);
