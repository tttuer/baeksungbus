// IndexedDB 초기화
function openDatabase() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('DdocksDB', 1);

        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains('ddocks')) {
                db.createObjectStore('ddocks', {keyPath: 'id'}); // id 필드를 키로 설정
            }
        };

        request.onsuccess = (event) => {
            resolve(event.target.result);
        };

        request.onerror = (event) => {
            reject(event.target.error);
        };
    });
}

// IndexedDB에 데이터 저장
async function saveToIndexedDB(ddocks) {
    const db = await openDatabase();
    const transaction = db.transaction('ddocks', 'readwrite');
    const store = transaction.objectStore('ddocks');

    ddocks.forEach((ddock, index) => {
        store.put({id: index, image: ddock.image}); // id와 이미지 데이터를 저장
    });

    return transaction.complete;
}

// IndexedDB에서 데이터 가져오기
async function getFromIndexedDB() {
    const db = await openDatabase();
    const transaction = db.transaction('ddocks', 'readonly');
    const store = transaction.objectStore('ddocks');

    return new Promise((resolve, reject) => {
        const request = store.getAll();

        request.onsuccess = () => {
            resolve(request.result);
        };

        request.onerror = (event) => {
            reject(event.target.error);
        };
    });
}

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
        // IndexedDB에서 데이터 확인
        const cachedData = await getFromIndexedDB();
        if (cachedData && cachedData.length > 0) {
            console.log('Using cached data from IndexedDB');
            await renderDdocksSequentially(cachedData);
            return; // 캐싱된 데이터로 렌더링 후 종료
        }

        // 서버에서 데이터 요청
        const response = await fetch('/api/ddocks'); // FastAPI 엔드포인트
        if (!response.ok) {
            throw new Error('Failed to fetch ddocks');
        }

        const data = await response.json();

        // 데이터를 IndexedDB에 저장
        await saveToIndexedDB(data.ddocks);

        // 데이터를 렌더링
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
