const pageSize = 20; // 한 페이지에 표시할 항목 수
let selectedQaId = null; // 현재 선택된 QA의 ID를 저장

// QA 데이터를 API에서 가져오는 함수
async function fetchQAs(page = 1) {
    const response = await fetch(`/api/notices?notice_type=NOTICE&page=${page}&page_size=${pageSize}`);
    const data = await response.json();
    renderQATable(data.notices);
    renderPagination(data.page, data.total_pages);
}

// 초기 로드 시 첫 번째 페이지 데이터를 불러오기 위해 호출
fetchQAs();

// QA 테이블을 생성하고 렌더링하는 함수
function renderQATable(notices) {
    const tableBody = document.getElementById("noticeTableBody");
    tableBody.innerHTML = "";

    notices.forEach(notice => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <th scope="row">${notice.num}</th>
            <td style="cursor: pointer;">${notice.title}${notice.attachment_filename ? '<i class="bi bi bi-file-earmark-text ms-2" title="첨부파일"></i>' : ''}</td>
            <td>${notice.writer}</td>
            <td>${notice.c_date}</td>
        `;

        // 제목 셀 클릭 이벤트
        row.querySelector("td").addEventListener("click", async () => {
            selectedQaId = notice.id;

            window.location.href = `/notice/detail?id=${notice.id}`;
        });

        tableBody.appendChild(row);
    });
}

// 페이지네이션 버튼을 생성하고 렌더링하는 함수
function renderPagination(currentPage, totalPages) {
    const pagination = document.getElementById("pagination");
    pagination.innerHTML = "";

    // Previous 버튼 생성
    const prevButton = document.createElement("li");
    prevButton.className = `page-item ${currentPage === 1 ? "disabled" : ""}`;
    prevButton.innerHTML = `
        <a class="page-link" href="#" aria-label="Previous">
            <span aria-hidden="true">&laquo;</span>
        </a>
    `;
    prevButton.addEventListener("click", () => {
        if (currentPage > 1) fetchQAs(currentPage - 1);
    });
    pagination.appendChild(prevButton);

    // 페이지 번호 생성
    for (let i = 1; i <= totalPages; i++) {
        const pageItem = document.createElement("li");
        pageItem.className = `page-item ${i === currentPage ? "active" : ""}`;
        pageItem.innerHTML = `<a class="page-link" href="#">${i}</a>`;
        pageItem.addEventListener("click", () => fetchQAs(i));
        pagination.appendChild(pageItem);
    }

    // Next 버튼 생성
    const nextButton = document.createElement("li");
    nextButton.className = `page-item ${currentPage === totalPages ? "disabled" : ""}`;
    nextButton.innerHTML = `
        <a class="page-link" href="#" aria-label="Next">
            <span aria-hidden="true">&raquo;</span>
        </a>
    `;
    nextButton.addEventListener("click", () => {
        if (currentPage < totalPages) fetchQAs(currentPage + 1);
    });
    pagination.appendChild(nextButton);
}

// 초기 페이지 로딩
document.addEventListener("DOMContentLoaded", () => fetchQAs());
