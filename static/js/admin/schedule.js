import {authFetch} from "/static/js/auth.js";

const pageSize = 20;
let currentPage = 1;
let attachedFiles = []; // 수정 모달에 첨부파일 목록을 저장하는 배열

// 스케줄 목록 가져오기
function fetchSchedules(page) {
    fetch(`/api/schedules?page=${page}&page_size=${pageSize}`)
        .then(response => response.json())
        .then(data => {
            renderTable(data.schedules);
            renderPagination(data.page, data.total_pages);
        })
        .catch(error => console.error("Error fetching schedules:", error));
}

// 테이블 렌더링 함수
function renderTable(schedules) {
    const tableBody = document.getElementById("schedule-table-body");
    tableBody.innerHTML = schedules.map(schedule => `
        <tr>
            <td>${schedule.num}</td>
            <td>${schedule.title}</td>
            <td class="text-end">
                <button class="btn btn-sm btn-primary edit-btn" data-id="${schedule.id}">수정</button>
            </td>
            <td class="text-end">
                <button class="btn btn-sm btn-danger delete-btn" data-id="${schedule.id}">삭제</button>
            </td>
        </tr>
    `).join("");

    // 수정 및 삭제 버튼에 이벤트 리스너 추가
    document.querySelectorAll(".edit-btn").forEach(button => {
        button.addEventListener("click", (e) => {
            const scheduleId = e.target.getAttribute("data-id");
            editSchedule(scheduleId);
        });
    });

    document.querySelectorAll(".delete-btn").forEach(button => {
        button.addEventListener("click", (e) => {
            const scheduleId = e.target.getAttribute("data-id");
            deleteSchedule(scheduleId);
        });
    });
}

function resetEditModal() {
    // 제목 필드 초기화
    document.getElementById('editTitle').value = '';
    document.getElementById('editId').value = '';

    // 첨부파일 배열 초기화
    attachedFiles = [];

    // 첨부파일 UI 초기화
    const fileContainer = document.getElementById("editAttachments");
    fileContainer.innerHTML = '';

    // 새로운 파일 입력 필드 초기화
    const newFileInputs = document.querySelectorAll('.new-file-input');
    newFileInputs.forEach(input => {
        input.value = '';
    });
}


// 수정 함수
function editSchedule(id) {
    resetEditModal();
    authFetch(`/api/schedules/${id}`)
        .then(response => response.json())
        .then(schedule => {
            // 모달에 데이터 채우기
            document.getElementById('editTitle').value = schedule.title;
            document.getElementById('editId').value = schedule.id;

            // Base64 데이터를 첨부파일 리스트로 변환
            attachedFiles = [];
            if (schedule.image_name1) attachedFiles.push({name: schedule.image_name1, data: schedule.image1});
            if (schedule.image_name2) attachedFiles.push({name: schedule.image_name2, data: schedule.image2});
            if (schedule.image_name3) attachedFiles.push({name: schedule.image_name3, data: schedule.image3});

            // 첨부파일 렌더링
            renderAttachments();

            // 수정 모달 열기
            const modal = new bootstrap.Modal(document.getElementById('editScheduleModal'));
            modal.show();
        })
        .catch(error => console.error("Error loading schedule:", error));
}

// 첨부파일 렌더링
function renderAttachments() {
    const fileContainer = document.getElementById("editAttachments");
    fileContainer.innerHTML = attachedFiles.map((file, index) => `
        <div class="d-flex align-items-center mb-2" data-index="${index}">
            <span>첨부파일${index + 1}: ${file.name || '삭제된 파일'}</span>
            <button type="button" class="btn btn-sm btn-outline-danger ms-2" onclick="removeFile(${index})">삭제</button>
        </div>
    `).join("");
}

// 전역에 removeFile 함수 추가
window.removeFile = function (index) {
    // 배열에서 해당 파일의 이름과 데이터를 빈 문자열로 설정
    attachedFiles[index].name = '';
    attachedFiles[index].data = '';

    // UI 업데이트
    renderAttachments();
};

function saveEditedSchedule() {
    const id = document.getElementById('editId').value;
    const title = document.getElementById('editTitle').value;
    const formData = new FormData();
    formData.append('title', title);

    // 기존 첨부파일 필드 추가 (빈 문자열은 서버에서 null로 처리)
    attachedFiles.forEach((file, i) => {
        formData.append(`image_name${i + 1}`, file.name); // 파일 이름이 빈 문자열이면 null로 처리할 예정
    });

    // 새롭게 첨부된 파일 처리
    const newFileInputs = document.querySelectorAll('.new-file-input');
    newFileInputs.forEach((input, i) => {
        if (input.files[0]) {
            formData.append(`image${i + 1}`, input.files[0]); // 새로운 파일을 FormData에 추가
        }
    });

    authFetch(`/api/schedules/${id}`, {
        method: 'PUT',
        body: formData
    })
        .then(response => {
            if (!response.ok) {
                throw new Error("Update failed");
            }
            alert("수정 완료!");
            fetchSchedules(currentPage); // 목록 갱신
            const modal = bootstrap.Modal.getInstance(document.getElementById('editScheduleModal'));
            modal.hide();
        })
        .catch(error => console.error("Error:", error));
}


// 삭제 함수
function deleteSchedule(id) {
    if (confirm("이 스케줄을 삭제하시겠습니까?")) {
        authFetch(`/api/schedules/${id}`, {
            method: "DELETE"
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error("삭제 실패");
                }
                alert("삭제 완료!");
                fetchSchedules(currentPage); // 삭제 후 목록 갱신
            })
            .catch(error => console.error("Error:", error));
    }
}

// 페이지네이션 렌더링
function renderPagination(current, totalPages) {
    const pagination = document.getElementById("pagination");
    pagination.innerHTML = "";

    const prevButton = document.createElement("li");
    prevButton.className = `page-item ${current === 1 ? "disabled" : ""}`;
    prevButton.innerHTML = `<a class="page-link" href="#">Previous</a>`;
    prevButton.addEventListener("click", () => {
        if (current > 1) fetchSchedules(current - 1);
    });
    pagination.appendChild(prevButton);

    for (let page = 1; page <= totalPages; page++) {
        const pageItem = document.createElement("li");
        pageItem.className = `page-item ${page === current ? "active" : ""}`;
        pageItem.innerHTML = `<a class="page-link" href="#">${page}</a>`;
        pageItem.addEventListener("click", () => fetchSchedules(page));
        pagination.appendChild(pageItem);
    }

    const nextButton = document.createElement("li");
    nextButton.className = `page-item ${current === totalPages ? "disabled" : ""}`;
    nextButton.innerHTML = `<a class="page-link" href="#">Next</a>`;
    nextButton.addEventListener("click", () => {
        if (current < totalPages) fetchSchedules(current + 1);
    });
    pagination.appendChild(nextButton);
}

// 새 글 작성 함수
function submitScheduleForm() {
    const form = document.getElementById('scheduleForm');
    const formData = new FormData(form);

    authFetch('/api/schedules', {
        method: 'POST',
        body: formData
    })
        .then(response => {
            if (!response.ok) {
                throw new Error("Request failed");
            }
            alert("작성 완료!");
            form.reset();
            const modal = bootstrap.Modal.getInstance(document.getElementById('scheduleModal'));
            modal.hide();
            fetchSchedules(1);  // 첫 번째 페이지부터 최신 리스트 불러오기
        })
        .catch(error => console.error('Error:', error));
}

// 초기 로드 시 이벤트 추가 및 첫 페이지 로드
document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("submit-schedule-btn").addEventListener("click", submitScheduleForm);
    document.getElementById("save-edit-btn").addEventListener("click", saveEditedSchedule);
    fetchSchedules(currentPage);
});
