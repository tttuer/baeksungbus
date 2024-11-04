const pageSize = 20; // 한 페이지에 표시할 항목 수
let selectedQaId = null; // 현재 선택된 QA의 ID를 저장

// QA 데이터를 API에서 가져오는 함수
async function fetchQAs(page = 1) {
    const qaType = document.getElementById("qaType").value; // qa_type 값을 읽음
    const response = await fetch(`/api/qas/?qa_type=${qaType}&page=${page}&page_size=${pageSize}`);
    const data = await response.json();
    renderQATable(data.qas);
    renderPagination(data.page, data.total_pages);
}

// 초기 로드 시 첫 번째 페이지 데이터를 불러오기 위해 호출
fetchQAs();

// 모달 초기화 함수
function resetPasswordModal() {
    const passwordInput = document.getElementById("passwordInput");
    const passwordFeedback = document.getElementById("passwordFeedback");

    // 초기화: 입력 필드와 오류 메시지 숨김
    passwordInput.classList.remove("is-invalid");
    passwordInput.value = ""; // 입력 필드 비우기
    passwordFeedback.style.display = "none";
}

// QA 테이블을 생성하고 렌더링하는 함수
function renderQATable(qas) {
    const tableBody = document.getElementById("qaTableBody");
    tableBody.innerHTML = "";

    qas.forEach(qa => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <th scope="row">${qa.num}</th>
            <td style="cursor: pointer;">${qa.title}${qa.hidden ? '<i class="bi bi-file-lock ms-2" title="비공개 글"></i>' : ''}${qa.attachment_filename ? '<i class="bi bi bi-file-earmark-text ms-2" title="첨부파일"></i>' : ''}</td>
            <td>${qa.writer}</td>
            <td>${qa.c_date}</td>
            <td>${qa.done ? "처리완료" : "처리중"}</td>
            <td>${qa.read_cnt}</td>
        `;

        // 제목 셀 클릭 이벤트
        row.querySelector("td").addEventListener("click", () => {
            if (qa.hidden) {
                // 비밀번호가 필요한 경우 ID를 설정하고 모달 표시
                selectedQaId = qa.id;
                resetPasswordModal(); // 모달 초기화
                const passwordModal = new bootstrap.Modal(document.getElementById("passwordModal"));
                passwordModal.show();
            } else {
                // 비공개 글이 아닌 경우 상세 페이지로 바로 이동
                window.location.href = `/qa/detail?id=${qa.id}`;
            }
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

// 비밀번호 확인 버튼 클릭 이벤트 추가
document.getElementById("checkPasswordButton").addEventListener("click", async () => {
    const password = document.getElementById("passwordInput").value;
    const passwordFeedback = document.getElementById("passwordFeedback");

    // 비밀번호 확인 API 호출
    const response = await fetch(`/api/qas/${selectedQaId}/check_password?password=${password}`);

    if (response.ok) {
        // 비밀번호가 맞으면 상세 페이지로 이동
        const passwordModal = bootstrap.Modal.getInstance(document.getElementById("passwordModal"));
        passwordModal.hide(); // 모달 닫기
        window.location.href = `/qa/detail?id=${selectedQaId}`;
    } else {
        // 비밀번호가 틀렸을 때 오류 메시지 표시
        passwordFeedback.style.display = "block";
        passwordFeedback.textContent = "비밀번호가 일치하지 않습니다.";
        document.getElementById("passwordInput").classList.add("is-invalid");
    }
});

// 초기 페이지 로딩
document.addEventListener("DOMContentLoaded", () => fetchQAs());
