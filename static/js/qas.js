const pageSize = 20  // 한 페이지에 표시할 항목 수

async function fetchQAs(page = 1) {
    const qaType = document.getElementById("qaType").value;  // qa_type 값을 읽음
    const response = await fetch(`/api/qas/?qa_type=${qaType}&page=${page}&page_size=${pageSize}`)
    const data = await response.json()
    renderQATable(data.qas)
    renderPagination(data.page, data.total_pages)
}

// 초기 로드 시 첫 번째 페이지 데이터를 불러오기 위해 호출
fetchQAs()

function renderQATable(qas) {
    const tableBody = document.getElementById("qaTableBody")
    tableBody.innerHTML = ""  // 기존 데이터 지우기
    qas.forEach(qa => {
        const row = document.createElement("tr")
        row.innerHTML = `
            <th scope="row">${qa.num}</th>
            <td>${qa.title}${qa.hidden ? '<i class="bi bi-file-lock ms-2" title="비공개 글"></i>' : ''}${qa.attachment_filename ? '<i class="bi bi bi-file-earmark-text" title="비공개 글"></i>' : ''}</td>
            <td>${qa.writer}</td>
            <td>${qa.c_date}</td>
            <td>${qa.done ? "처리완료" : "처리중"}</td>
            <td>${qa.read_cnt}</td>
        `
        tableBody.appendChild(row)
    })
}

function renderPagination(currentPage, totalPages) {
    const pagination = document.getElementById("pagination")
    pagination.innerHTML = ""

    // Previous 버튼 생성
    const prevButton = document.createElement("li")
    prevButton.className = `page-item ${currentPage === 1 ? "disabled" : ""}`
    prevButton.innerHTML = `
        <a class="page-link" href="#" aria-label="Previous">
            <span aria-hidden="true">&laquo;</span>
        </a>
    `
    prevButton.addEventListener("click", () => {
        if (currentPage > 1) fetchQAs(currentPage - 1)
    })
    pagination.appendChild(prevButton)

    // 페이지 번호 생성
    for (let i = 1; i <= totalPages; i++) {
        const pageItem = document.createElement("li")
        pageItem.className = `page-item ${i === currentPage ? "active" : ""}`
        pageItem.innerHTML = `<a class="page-link" href="#">${i}</a>`
        pageItem.addEventListener("click", () => fetchQAs(i))
        pagination.appendChild(pageItem)
    }

    // Next 버튼 생성
    const nextButton = document.createElement("li")
    nextButton.className = `page-item ${currentPage === totalPages ? "disabled" : ""}`
    nextButton.innerHTML = `
        <a class="page-link" href="#" aria-label="Next">
            <span aria-hidden="true">&raquo;</span>
        </a>
    `
    nextButton.addEventListener("click", () => {
        if (currentPage < totalPages) fetchQAs(currentPage + 1)
    })
    pagination.appendChild(nextButton)
}

// 초기 페이지 로딩
document.addEventListener("DOMContentLoaded", () => fetchQAs())
