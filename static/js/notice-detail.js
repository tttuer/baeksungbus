document.addEventListener("DOMContentLoaded", async function () {
    const quill = new Quill('#editor', {
        theme: 'snow',
        modules: {
            toolbar: false  // 툴바 비활성화하여 읽기 전용으로 설정
        },
        readOnly: true  // Quill을 읽기 전용으로 설정
    });

    const commentQuill = new Quill('#commentEditor', {
        theme: 'snow',
        modules: {
            toolbar: false  // 툴바 비활성화하여 읽기 전용으로 설정
        },
        readOnly: true  // 댓글 Quill도 읽기 전용으로 설정
    });

    const urlParams = new URLSearchParams(window.location.search);
    const id = urlParams.get("id");

    if (id) {
        try {
            const response = await fetch(`/api/notices/${id}`);
            if (response.ok) {
                const data = await response.json();

                const noticeType = data.notice_type;
                const pageTitle = document.getElementById("pageTitle");

                // qaType 값에 따라 제목을 변경
                pageTitle.textContent = noticeType === "NOTICE" ? "공지사항" : (noticeType === "LOST" ? "분실물문의" : "문의");

                // 필드에 데이터 채우기
                document.getElementById("title").value = data.title;
                document.getElementById("writer").value = data.writer;
                document.getElementById("c_date").value = data.c_date;

                // 첨부파일이 이미지 파일일 경우 Quill 최상단에 추가
                if (data.attachment && data.attachment_filename.match(/\.(jpg|jpeg|png|gif)$/i)) {
                    const imageHTML = `<p><img src="data:image/png;base64,${data.attachment}" style="max-width: 100%;"></p>`;
                    quill.clipboard.dangerouslyPasteHTML(0, imageHTML);  // 최상단에 이미지 추가
                }

                // Quill에 본문 내용 설정
                quill.clipboard.dangerouslyPasteHTML(quill.getLength(), data.content);  // 본문 내용을 이미지 아래에 추가

                // 첨부파일이 있는 경우에만 다운로드 링크 설정
                if (data.attachment && data.attachment_filename) {
                    const downloadAttachment = document.createElement("a");
                    downloadAttachment.id = "downloadAttachment";
                    downloadAttachment.href = `data:application/octet-stream;base64,${data.attachment}`;
                    downloadAttachment.download = data.attachment_filename;
                    downloadAttachment.textContent = `${data.attachment_filename} 다운로드`;
                    downloadAttachment.style.display = "block";
                    downloadAttachment.style.marginTop = "10px";

                    // Quill 에디터 바로 아래에 첨부파일 다운로드 링크 추가
                    const editorContainer = document.getElementById("editor");
                    editorContainer.parentNode.insertBefore(downloadAttachment, editorContainer.nextSibling);
                }

                // 동적으로 Quill 높이 조정 (내용이 완전히 적용된 후)
                setTimeout(adjustQuillHeight, 100);  // 조금의 지연 후 높이 조정

                // 글 목록 버튼의 링크를 qaType에 따라 설정
                const backToListButton = document.getElementById("backToListButton");
                backToListButton.addEventListener("click", function () {
                    window.location.href = noticeType === "NOTICE" ? "/notice" : "/lost";
                });

            } else {
                alert("글을 불러오는 데 실패했습니다.");
            }
        } catch (error) {
            console.error("Error fetching QA:", error);
            alert("서버와 통신 중 문제가 발생했습니다.");
        }
    }

    // Quill 내용에 따라 높이 조정
    function adjustQuillHeight() {
        const editorContainer = document.getElementById("editor");
        const contentHeight = editorContainer.scrollHeight;
        editorContainer.style.height = `${Math.max(contentHeight, 200)}px`;
    }

    // Quill 내용 변화에 따라 높이 자동 조정
    quill.on('text-change', adjustQuillHeight);
});
