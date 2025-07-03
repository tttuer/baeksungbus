import {authFetch} from "/static/js/auth.js";

const pageSize = 20;
let currentPage = 1;
let attachedFiles = []; // 수정 모달에 첨부파일 목록을 저장하는 배열
let quillEditor = null; // 글쓰기 모달용 Quill
let quillEditEditor = null; // 수정 모달용 Quill

// 스케줄 목록 가져오기
function fetchNotices(page) {
    fetch(`/api/notices?page=${page}&page_size=${pageSize}`)
        .then(response => response.json())
        .then(data => {
            renderPagination(data.page, data.total_pages)
            renderTable(data.notices);
        })
        .catch(error => console.error("Error fetching notices:", error));
}

// 테이블 렌더링 함수
function renderTable(notices) {
    const tableBody = document.getElementById("notice-table-body");
    tableBody.innerHTML = notices.map(notice => `
        <tr>
            <td>${notice.num}</td>
            <td>${notice.title}</td>
            <td class="text-end">
                <button class="btn btn-sm btn-primary edit-btn" data-id="${notice.id}">수정</button>
            </td>
            <td class="text-end">
                <button class="btn btn-sm btn-danger delete-btn" data-id="${notice.id}">삭제</button>
            </td>
        </tr>
    `).join("");

    // 수정 버튼 이벤트 추가
    document.querySelectorAll(".edit-btn").forEach(button => {
        button.addEventListener("click", (e) => {
            const noticeId = e.target.getAttribute("data-id");
            editNotice(noticeId);
        });
    });

    // 삭제 버튼 이벤트 추가
    document.querySelectorAll(".delete-btn").forEach(button => {
        const noticeId = button.getAttribute("data-id");
        button.addEventListener("click", () => deleteNotice(noticeId));
    });
}

// 🔹 글쓰기 모달이 열릴 때 Quill 에디터 초기화
document.getElementById("noticeModal").addEventListener("shown.bs.modal", () => {
    if (!quillEditor) {
        quillEditor = new Quill("#editor", {
            theme: "snow", placeholder: "내용을 입력하세요...", modules: {
                toolbar: [[{header: [1, 2, false]}], ["bold", "italic", "underline"], ["image", "code-block"], [{list: "ordered"}, {list: "bullet"}], ["link"], ["clean"],],
            },
        });
    } else {
        quillEditor.setContents([]); // 초기화
    }
});

// 🔹 글쓰기 모달이 닫힐 때 초기화
document.getElementById("noticeModal").addEventListener("hidden.bs.modal", () => {
    document.getElementById("title").value = "";
    if (quillEditor) {
        quillEditor.setContents([]);
    }
});

// 🔹 수정 모달 초기화 및 Quill 적용
function editNotice(id) {
    authFetch(`/api/notices/${id}`)
        .then(response => response.json())
        .then(notice => {
            // 제목 설정
            document.getElementById("editTitle").value = notice.title;
            document.getElementById("editId").value = notice.id;

            // Quill 에디터 초기화 (최초 1회만 실행)
            if (!quillEditEditor) {
                quillEditEditor = new Quill("#editEditor", {
                    theme: "snow",
                });
            } else {
                quillEditEditor.setContents([]); // 기존 내용 초기화
            }

            // 첨부파일이 이미지일 경우 추가
            if (notice.attachment && notice.attachment_filename.match(/\.(jpg|jpeg|png|gif)$/i)) {
                const imageHTML = `<p><img src="data:image/png;base64,${notice.attachment}" style="max-width: 100%; display: block; margin: 10px 0;"></p>`;
                quillEditEditor.clipboard.dangerouslyPasteHTML(quillEditEditor.getLength(), imageHTML);
            }

            // 기존 내용 불러오기
            if (notice.content) {
                quillEditEditor.clipboard.dangerouslyPasteHTML(quillEditEditor.getLength(), notice.content);
            }


            // 수정 모달 열기
            const modal = new bootstrap.Modal(document.getElementById("editNoticeModal"));
            modal.show();
        })
        .catch(error => console.error("Error loading notice:", error));
}

// 🔹 수정 모달이 닫힐 때 내용 초기화
document.getElementById("editNoticeModal").addEventListener("hidden.bs.modal", () => {
    document.getElementById("editTitle").value = "";
    if (quillEditEditor) {
        quillEditEditor.setContents([]);
    }
});

// 🔹 수정된 글 저장 (JSON 방식)
function saveEditedNotice() {
    const id = document.getElementById("editId").value;
    const title = document.getElementById("editTitle").value;
    const content = quillEditEditor ? quillEditEditor.root.innerHTML : "";

    // 필요한 경우 유효성 검사 추가
    if (!title.trim()) {
        alert("제목을 입력하세요.");
        return;
    }
    if (content.trim() === "<p><br></p>") {
        alert("내용을 입력하세요.");
        return;
    }

    const notice = {
        title: title, content: content
    };

    authFetch(`/api/notices/${id}`, {
        method: "PATCH", headers: {
            "Content-Type": "application/json"
        }, body: JSON.stringify(notice)
    })
        .then(response => {
            if (!response.ok) {
                throw new Error("Update failed");
            }
            alert("수정 완료!");
            fetchNotices(currentPage);
            const modal = bootstrap.Modal.getInstance(document.getElementById("editNoticeModal"));
            modal.hide();
        })
        .catch(error => console.error("Error:", error));
}


// 🔹 삭제 함수
function deleteNotice(id) {
    if (confirm("이 공지를 삭제하시겠습니까?")) {
        authFetch(`/api/notices/${id}`, {
            method: "DELETE"
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error("삭제 실패");
                }
                alert("삭제 완료!");
                fetchNotices(currentPage);
            })
            .catch(error => console.error("Error:", error));
    }
}

// 🔹 페이지네이션 렌더링
function renderPagination(current, totalPages) {
    const pagination = document.getElementById("pagination");
    pagination.innerHTML = "";

    for (let page = 1; page <= totalPages; page++) {
        const pageItem = document.createElement("li");
        pageItem.className = `page-item ${page === current ? "active" : ""}`;
        pageItem.innerHTML = `<a class="page-link" href="#">${page}</a>`;
        pageItem.addEventListener("click", () => fetchNotices(page));
        pagination.appendChild(pageItem);
    }
}

function submitNoticeForm() {
    const title = document.getElementById("title").value;
    const content = quillEditor ? quillEditor.root.innerHTML : "";

    if (!title.trim()) {
        alert("제목을 입력하세요.");
        return;
    }

    if (content.trim() === "<p><br></p>") {
        alert("내용을 입력하세요.");
        return;
    }

    // FormData 생성
    const formData = new FormData();
    formData.append("title", title);
    formData.append("content", content);

    // 파일 첨부 처리
    const fileInput = document.querySelector("input[name='image1']");
    if (fileInput.files.length > 0) {
        formData.append("attachment", fileInput.files[0]);
    }

    // API 요청 (Content-Type 헤더는 FormData 사용 시 브라우저가 자동 설정)
    authFetch("/api/notices", {
        method: "POST", body: formData
    })
        .then(response => {
            if (!response.ok) {
                throw new Error("Request failed");
            }
            alert("작성 완료!");
            document.getElementById("noticeForm").reset();
            quillEditor.setContents([]); // Quill 내용 리셋
            const modal = bootstrap.Modal.getInstance(document.getElementById("noticeModal"));
            modal.hide();
            fetchNotices(1);  // 첫 번째 페이지부터 최신 리스트 불러오기
        })
        .catch(error => console.error("Error:", error));
}


// 🔹 초기 로드 시 이벤트 추가 및 첫 페이지 로드
document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("submit-notice-btn").addEventListener("click", submitNoticeForm);
    document.getElementById("save-edit-btn").addEventListener("click", saveEditedNotice);
    fetchNotices(currentPage);
});
