// QA 데이터를 저장할 변수
let qaData = null;

// QA 데이터를 API에서 가져와 qaData에 저장하는 함수
async function loadQAData() {
    const urlParams = new URLSearchParams(window.location.search);
    const id = urlParams.get("id");

    if (id) {
        try {
            const response = await fetch(`/api/qas/${id}`);
            if (response.ok) {
                qaData = await response.json(); // 데이터를 qaData 변수에 저장
                populateFormFields(); // 폼 필드 채우기

                // qaData.qa_type에 따라 redirect_url을 설정
                const redirectUrlInput = document.getElementById("redirect_url");
                redirectUrlInput.value = qaData.qa_type === "CUSTOMER" ? "/qa" : "/lost";
            } else {
                alert("글을 불러오는 데 실패했습니다.");
            }
        } catch (error) {
            console.error("Error fetching QA:", error);
            alert("서버와 통신 중 문제가 발생했습니다.");
        }
    }
}

// 폼 필드에 데이터를 채워 넣는 함수
function populateFormFields() {
    if (!qaData) return; // qaData가 없으면 중단

    const quill = new Quill('#editor', {theme: 'snow'});

    // Quill 에디터 초기 내용 설정 및 높이 조정
    quill.root.innerHTML = qaData.content || '';
    adjustQuillHeight();

    document.getElementById("writer").value = qaData.writer;
    document.getElementById("email").value = qaData.email || '';
    document.getElementById("title").value = qaData.title;
    document.getElementById("password").value = qaData.password;

    // Display the attachment name and preview if exists
    if (qaData.attachment_filename) {
        document.getElementById("attachmentName").textContent = `기존 첨부 파일: ${qaData.attachment_filename}`;
        document.getElementById("keepAttachment").value = "true";
        document.getElementById("removeAttachment").classList.remove("d-none");

        if (qaData.attachment && /\.(jpg|jpeg|png|gif)$/i.test(qaData.attachment_filename)) {
            const attachmentPreview = document.createElement("img");
            attachmentPreview.src = `data:image/png;base64,${qaData.attachment}`;
            attachmentPreview.alt = qaData.attachment_filename;
            attachmentPreview.style.maxWidth = "100%";
            attachmentPreview.style.marginTop = "10px";
        }
    }

    document.getElementById("hidden").checked = qaData.hidden;

    // Quill 내용이 변경될 때마다 높이 자동 조정
    quill.on('text-change', adjustQuillHeight);
}

// Quill 높이 동적으로 조정 함수
function adjustQuillHeight() {
    const editorContainer = document.getElementById("editor");
    const contentHeight = editorContainer.scrollHeight;
    editorContainer.style.height = `${Math.max(contentHeight, 200)}px`; // 최소 200px 유지
}

// 파일 선택 시 파일 이름 표시 업데이트 및 keepAttachment 설정 제거
document.getElementById("attachment").addEventListener("change", (event) => {
    document.getElementById("attachmentName").textContent = event.target.files.length ? `첨부 파일: ${event.target.files[0].name}` : "선택된 파일 없음";
    document.getElementById("keepAttachment").value = event.target.files.length ? "false" : "true";
    document.getElementById("removeAttachment").classList.add("d-none");
});

// 첨부파일 삭제 버튼 클릭 이벤트
document.getElementById("removeAttachment").addEventListener("click", () => {
    document.getElementById("attachment").value = "";
    document.getElementById("attachmentName").textContent = "선택된 파일 없음";
    document.getElementById("keepAttachment").value = "false";
    document.getElementById("removeAttachment").classList.add("d-none");
    document.getElementById("attachmentPreviewContainer").innerHTML = "";
});

// 폼 제출 시 서버에 수정 요청 보내기
document.getElementById("qaForm").addEventListener("submit", async function (event) {
    event.preventDefault();

    const urlParams = new URLSearchParams(window.location.search);
    const id = urlParams.get("id");

    const formData = new FormData(this);
    formData.append("content", document.querySelector("#editor .ql-editor").innerHTML);

    try {
        const response = await fetch(`/api/qas/${id}`, {
            method: "PATCH",
            body: formData
        });

        if (response.ok) {
            alert("글이 성공적으로 수정되었습니다.");
            window.location.href = formData.get("redirect_url");
        } else {
            alert("글 수정에 실패했습니다.");
        }
    } catch (error) {
        console.error("Error updating QA:", error);
        alert("서버 오류가 발생했습니다. 다시 시도해주세요.");
    }
});

// 페이지 로드 시 QA 데이터 로드
document.addEventListener("DOMContentLoaded", function () {
    loadQAData();
});
