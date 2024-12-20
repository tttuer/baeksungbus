// IndexedDB 초기화
function openDatabase() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('DdocksDB', 1);

        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains('ddocks')) {
                db.createObjectStore('ddocks', {keyPath: 'id'}); // id 필드를 키로 설정
            }
            if (!db.objectStoreNames.contains('meta')) {
                db.createObjectStore('meta', {keyPath: 'key'}); // 메타데이터 저장
            }
        };

        request.onsuccess = (event) => resolve(event.target.result);
        request.onerror = (event) => reject(event.target.error);
    });
}

// 해시 생성 함수
function generateHash(data) {
    return crypto.subtle.digest('SHA-256', new TextEncoder().encode(JSON.stringify(data)))
        .then((hashBuffer) => Array.from(new Uint8Array(hashBuffer))
            .map((b) => b.toString(16).padStart(2, '0'))
            .join(''));
}

// IndexedDB에 데이터 저장
async function saveToIndexedDB(ddocks, hash) {
    const db = await openDatabase();

    const transaction = db.transaction(['ddocks', 'meta'], 'readwrite');
    const ddockStore = transaction.objectStore('ddocks');
    const metaStore = transaction.objectStore('meta');

    ddocks.forEach((ddock) => ddockStore.put(ddock));
    metaStore.put({key: 'hash', value: hash});

    return transaction.complete;
}

// IndexedDB에서 데이터 가져오기
async function getFromIndexedDB() {
    const db = await openDatabase();
    const transaction = db.transaction(['ddocks', 'meta'], 'readonly');
    const ddockStore = transaction.objectStore('ddocks');
    const metaStore = transaction.objectStore('meta');

    const [data, meta] = await Promise.all([
        new Promise((resolve) => {
            const request = ddockStore.getAll();
            request.onsuccess = () => resolve(request.result);
        }),
        new Promise((resolve) => {
            const request = metaStore.get('hash');
            request.onsuccess = () => resolve(request.result?.value || null);
        })
    ]);

    return {data, hash: meta};
}

// 서버에서 데이터 가져오기
async function fetchFromServer() {
    const response = await fetch('/api/ddocks'); // FastAPI 엔드포인트
    if (!response.ok) throw new Error('Failed to fetch ddocks');
    const data = await response.json();
    return data.ddocks;
}

// ddocks 데이터를 가져오는 함수
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
        const {data: cachedData, hash: cachedHash} = await getFromIndexedDB();

        if (cachedData && cachedHash) {
            console.log('Using cached data from IndexedDB');
            await renderDdocksSequentially(cachedData);

            // 서버 데이터와 해시 비교
            const serverData = await fetchFromServer();
            const serverHash = await generateHash(serverData);

            if (serverHash !== cachedHash) {
                console.log('Server data updated, refreshing cache');
                await saveToIndexedDB(serverData, serverHash);
                await renderDdocksSequentially(serverData);
            }
        } else {
            console.log('No cached data, fetching from server');
            const serverData = await fetchFromServer();
            const serverHash = await generateHash(serverData);
            await saveToIndexedDB(serverData, serverHash);
            await renderDdocksSequentially(serverData);
        }
    } catch (error) {
        console.error('Error:', error);
        editor.innerHTML = '<p>Failed to load data.</p>';
    } finally {
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
            img.style = 'max-width: 100%; margin-bottom: 10px;';

            await new Promise((resolve) => (img.onload = () => resolve()));
            editor.appendChild(img);

            await new Promise((resolve) => setTimeout(resolve, 200)); // 지연 시간 추가
        }
    }
}

// 페이지 로드 시 ddocks 데이터를 가져옴
document.addEventListener('DOMContentLoaded', fetchDdocks);
