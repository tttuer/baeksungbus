import {authFetch} from "/static/js/auth.js";

const apiUrl = "/api/qas"; // API URL
const tableBody = document.getElementById("qa-table-body");
const loadingSpinner = document.getElementById("loading-spinner");
const filterSelect = document.querySelector(".form-select");
let currentQaId = null; // 현재 선택된 QA ID 저장
let quillCommentEditor = null; // Quill Editor 객체
let existingAnswerId = null; // 기존 답변 ID 저장
let selectedValue = null;

let allQAs = []; // 전체 데이터를 저장할 변수

// 로딩 스피너 표시/숨김 함수
const showSpinner = () => {
    loadingSpinner.style.setProperty("display", "flex", "important");
};

const hideSpinner = () => {
    loadingSpinner.style.setProperty("display", "none", "important");
};

// 답변 작성 버튼 클릭 이벤트
const attachAnswerWriteEvent = () => {
    const answerWriteButton = document.getElementById("answerWrite");
    answerWriteButton.addEventListener("click", async () => {
        if (!currentQaId) {
            alert("QA ID를 확인할 수 없습니다.");
            return;
        }

        const content = quillCommentEditor.root.innerHTML.trim(); // Quill Editor의 HTML 내용 가져오기
        if (!content || content === "<p><br></p>") {
            alert("답변 내용을 입력하세요.");
            return;
        }

        try {
            if (existingAnswerId) {
                // 이미 답변이 있는 경우 PATCH 요청
                const response = await authFetch(`/api/answers/${existingAnswerId}`, {
                    method: "PATCH",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({content}),
                });

                if (response.ok) {
                    const result = await response.json();
                    alert("답변이 성공적으로 수정되었습니다!");
                } else {
                    const error = await response.json();
                    alert(`오류: ${error.detail}`);
                }
            } else {
                // 답변이 없는 경우 POST 요청
                const response = await authFetch(`/api/answers?qa_id=${currentQaId}`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({content}),
                });

                if (response.ok) {
                    const result = await response.json();
                    alert("답변이 성공적으로 등록되었습니다!");
                } else {
                    const error = await response.json();
                    alert(`오류: ${error.detail}`);
                }
            }

            await fetchQAs(1, selectedValue);
            const modal = bootstrap.Modal.getInstance(document.getElementById("detailModal"));
            modal.hide(); // 모달 닫기
        } catch (error) {
            console.error("API 요청 실패:", error);
            alert("서버 오류가 발생했습니다.");
        }
    });
};

// 답변 삭제 버튼 클릭 이벤트
const attachAnswerDeleteEvent = () => {
    const answerDeleteButton = document.getElementById("answerDelete");
    answerDeleteButton.addEventListener("click", async () => {
        if (!currentQaId) {
            alert("QA ID를 확인할 수 없습니다.");
            return;
        }

        const content = quillCommentEditor.root.innerHTML.trim(); // Quill Editor의 HTML 내용 가져오기
        if (!content || content === "<p><br></p>") {
            alert("답변 내용을 입력하세요.");
            return;
        }

        try {
            if (existingAnswerId) {
                // 이미 답변이 있는 경우 DELETE 요청
                const response = await authFetch(`/api/answers/${existingAnswerId}`, {
                    method: "DELETE",
                });

                if (response.ok) {
                    const result = await response.json();
                    alert("답변이 성공적으로 삭제되었습니다!");
                } else {
                    const error = await response.json();
                    alert(`오류: ${error.detail}`);
                }
            } else {
                alert('답변이 존재하지 않습니다.');
            }

            await fetchQAs(selectedValue);
            const modal = bootstrap.Modal.getInstance(document.getElementById("detailModal"));
            modal.hide(); // 모달 닫기
        } catch (error) {
            console.error("API 요청 실패:", error);
            alert("서버 오류가 발생했습니다.");
        }
    });
};


// 모달 동적으로 생성 함수
const createDynamicModal = (id, hasAnswer) => {
    // 기존 모달 제거
    const existingModal = document.getElementById("detailModal");
    if (existingModal) {
        existingModal.remove();
    }

    // 답변 삭제 버튼 HTML: 답변이 있을 때만 생성
    const answerDeleteButtonHTML = hasAnswer
        ? `<button type="button" class="btn btn-outline-dark" id="answerDelete" style="margin-left: 4px">답변 삭제</button>`
        : "";

    // 새로운 모달 생성
    const modalHTML = `
        <div class="modal fade" id="detailModal" tabindex="-1" aria-labelledby="detailModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="detailModalLabel">QA 상세 보기</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <form>
                            <div class="mb-3">
                                <label for="writer" class="form-label">작성자</label>
                                <input type="text" class="form-control" id="writer" readonly>
                            </div>
                            <div class="mb-3">
                                <label for="email" class="form-label">이메일</label>
                                <input type="email" class="form-control" id="email" readonly>
                            </div>
                            <div class="mb-3">
                                <label for="title" class="form-label">제목</label>
                                <input type="text" class="form-control" id="title" readonly>
                            </div>
                            <div class="mb-3">
                                <label for="c_date" class="form-label">작성일</label>
                                <input type="text" class="form-control" id="c_date" readonly>
                            </div>
                            <div class="mb-3" id="editorSection">
                                <label for="editor" class="form-label">내용</label>
                                <div id="editor" style="min-height: 200px; background-color: #ffffff; border: 1px solid #ced4da; border-radius: 0.375rem;"></div>
                            </div>
                            <div id="commentSection" class="col-12" style="display: none;">
                                <label for="commentEditor" class="form-label">답변</label>
                                <div id="commentEditor"
                                     style="min-height: 200px; background-color: #ffffff; border: 1px solid #ced4da; border-radius: 0.375rem;"></div>
                            </div>
                            <hr class="my-4" id="answerhr" style="display: none;">
                            <div class="d-flex justify-content-end mb-2" style="margin: 0;">
                                <button type="button" class="btn btn-outline-dark" id="answerWrite" style="margin-left: 4px">답변 작성</button>
                                ${answerDeleteButtonHTML}
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML("beforeend", modalHTML);
};

// 상세 보기 모달 표시
const showDetailModal = async (id) => {
    try {

        currentQaId = id; // 선택된 QA ID 저장
        existingAnswerId = null; // 기존 답변 ID 초기화

        const quill = new Quill('#editor', {
            theme: 'snow',
            modules: {
                toolbar: false, // 툴바 비활성화하여 읽기 전용으로 설정
            },
            readOnly: true, // Quill을 읽기 전용으로 설정
        });

        // API 호출로 상세 정보 가져오기
        const response = await authFetch(`${apiUrl}/${id}`);
        if (!response.ok) {
            throw new Error("Failed to fetch QA details");
        }
        const data = await response.json();

        // 답변 존재 여부 판단
        const hasAnswer = data.answers && data.answers.length > 0;

        createDynamicModal(id, hasAnswer); // 새로운 모달 동적으로 생성


        // 모달 내 입력 필드에 데이터 채우기
        document.getElementById("writer").value = data.writer || "";
        document.getElementById("email").value = data.email || "";
        document.getElementById("title").value = data.title || "";
        document.getElementById("c_date").value = data.c_date || "";

        // Quill 에디터 초기화
        quill.setContents([]); // 기존 내용을 초기화


        // 첨부파일이 이미지 파일일 경우 본문 아래에 추가
        if (data.attachment && data.attachment_filename.match(/\.(jpg|jpeg|png|gif)$/i)) {
            const imageHTML = `<p><img src="data:image/png;base64,${data.attachment}" style="max-width: 100%; display: block; margin: 10px 0;"></p>`;
            quill.clipboard.dangerouslyPasteHTML(quill.getLength(), imageHTML);
        }

        // 본문 내용 설정
        if (data.content) {
            quill.clipboard.dangerouslyPasteHTML(quill.getLength(), `<p>${data.content}</p>`);
        }

        // Quill Editor 초기화 (답변 작성용)
        quillCommentEditor = new Quill("#commentEditor", {
            theme: "snow",

        });

        // 댓글 섹션 표시 (예: 답변 내용)
        if (hasAnswer) {
            existingAnswerId = data.answers[0].id

            quillCommentEditor.setContents([]); // 이전 답변 초기화

            // document.getElementById("commentSection").style.display = "block";
            quillCommentEditor.clipboard.dangerouslyPasteHTML(0, data.answers[0].content || "");

            const answerDeleteButton = document.getElementById("answerDelete");
            answerDeleteButton.onclick = async () => {
                try {
                    if (!existingAnswerId) {
                        alert("삭제할 답변이 없습니다.");
                        return;
                    }
                    const response = await authFetch(`/api/answers/${existingAnswerId}`, {
                        method: "DELETE",
                    });
                    if (response.ok) {
                        await response.json();
                        alert("답변이 성공적으로 삭제되었습니다!");
                        // 삭제 후 필요한 후속 처리 (예: 모달 내용 갱신)
                    } else {
                        const error = await response.json();
                        alert(`오류: ${error.detail}`);
                    }

                    await fetchQAs(1, selectedValue);
                    const modal = bootstrap.Modal.getInstance(document.getElementById("detailModal"));
                    modal.hide(); // 모달 닫기
                } catch (error) {
                    console.error("답변 삭제 API 요청 실패:", error);
                    alert("서버 오류가 발생했습니다.");
                }
            };
        }


        // 댓글 섹션 표시
        document.getElementById("commentSection").style.display = "block";

        // 모달 표시
        const modal = new bootstrap.Modal(document.getElementById("detailModal"));
        modal.show();

        attachAnswerWriteEvent()
        // attachAnswerDeleteEvent()

    } catch (error) {
        console.error("Error fetching QA details:", error);
        alert("상세 정보를 가져오지 못했습니다.");
    }
};

// 테이블 행 클릭 이벤트 추가
const attachRowClickEvents = () => {
    document.querySelectorAll("#qa-table-body tr").forEach((row) => {
        row.addEventListener("click", () => {
            const id = row.getAttribute("data-id"); // 데이터 ID 가져오기
            showDetailModal(id);
        });
    });
};

// 데이터 렌더링 함수 (서버에서 받은 데이터를 그대로 렌더링)
const renderQAs = () => {
    tableBody.innerHTML = allQAs
        .map((qa) => `
            <tr data-id="${qa.id}">
                <td>${qa.num}</td>
                <td>${qa.title}</td>
                <td class="text-center">${qa.c_date}</td>
                <td class="text-center">${qa.done ? "완료" : "진행 중"}</td>
                <td class="text-center">${qa.read_cnt}</td>
            </tr>
        `)
        .join("");

    if (allQAs.length === 0) {
        tableBody.innerHTML = `<tr><td colspan="5" class="text-center">데이터가 없습니다.</td></tr>`;
    }

    attachRowClickEvents();
};

// 데이터 가져오기
const fetchQAs = async (page = 1, filter = "all") => {
    try {
        showSpinner();

        // 기본 쿼리 파라미터: qa_type, page, page_size
        let queryParams = `?qa_type=CUSTOMER&page=${page}&page_size=20`;

        // filter 값에 따른 done 파라미터 추가
        if (filter === "0") {
            queryParams += `&done=false`;
        } else if (filter === "1") {
            queryParams += `&done=true`;
        }

        const response = await authFetch(`${apiUrl}${queryParams}`);
        const data = await response.json();

        allQAs = data.qas; // 전체 데이터를 저장
        renderQAs(); // 초기 전체 데이터 렌더링

        // 페이지네이션 렌더링 (API에서 total_pages 값을 함께 반환한다고 가정)
        renderPagination(page, data.total_pages);
    } catch (error) {
        console.error("Error fetching QAs:", error);
    } finally {
        hideSpinner();
    }
};

// 페이지네이션 렌더링 함수
function renderPagination(current, totalPages) {
    const pagination = document.getElementById("pagination");
    pagination.innerHTML = "";

    // 이전 버튼 생성
    const prevButton = document.createElement("li");
    prevButton.className = `page-item ${current === 1 ? "disabled" : ""}`;
    prevButton.innerHTML = `<a class="page-link" href="#">Previous</a>`;
    prevButton.addEventListener("click", () => {
        if (current > 1) fetchQAs(current - 1, selectedValue);
    });
    pagination.appendChild(prevButton);

    // 페이지 번호 버튼 생성
    for (let page = 1; page <= totalPages; page++) {
        const pageItem = document.createElement("li");
        pageItem.className = `page-item ${page === current ? "active" : ""}`;
        pageItem.innerHTML = `<a class="page-link" href="#">${page}</a>`;
        pageItem.addEventListener("click", () => fetchQAs(page, selectedValue));
        pagination.appendChild(pageItem);
    }

    // 다음 버튼 생성
    const nextButton = document.createElement("li");
    nextButton.className = `page-item ${current === totalPages ? "disabled" : ""}`;
    nextButton.innerHTML = `<a class="page-link" href="#">Next</a>`;
    nextButton.addEventListener("click", () => {
        if (current < totalPages) fetchQAs(current + 1, selectedValue);
    });
    pagination.appendChild(nextButton);
}

filterSelect.addEventListener("change", () => {
    selectedValue = filterSelect.value;
    fetchQAs(1, selectedValue);
});

// Initialize the app
document.addEventListener("DOMContentLoaded", () => {
    fetchQAs(); // 기본적으로 전체 데이터 가져오기
});
