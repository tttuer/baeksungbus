document.addEventListener("DOMContentLoaded", async function () {
    const urlParams = new URLSearchParams(window.location.search);
    const id = urlParams.get("id");

    if (id) {
        try {
            const response = await fetch(`/api/qas/${id}`);
            if (response.ok) {
                const data = await response.json();

                const qaType = data.qa_type;
                const pageTitle = document.getElementById("pageTitle");

                // qaType 값에 따라 제목을 변경
                if (qaType === "CUSTOMER") {
                    pageTitle.textContent = "고객문의";
                } else if (qaType === "LOST") {
                    pageTitle.textContent = "분실물문의";
                } else {
                    pageTitle.textContent = "문의";
                }

                // 필드에 데이터 채우기
                document.getElementById("title").value = data.title;
                document.getElementById("writer").value = data.writer;
                document.getElementById("c_date").value = data.c_date;

                // HTML로 콘텐츠 렌더링
                const contentElement = document.getElementById("content");
                contentElement.innerHTML = data.content;  // HTML로 렌더링

                // 첨부파일 미리보기 설정
                if (data.attachment && data.attachment_filename) {
                    const previewContainer = document.createElement("div");
                    previewContainer.classList.add("mb-3");

                    if (data.attachment_filename.match(/\.(jpg|jpeg|png|gif)$/i)) {  // 이미지 파일인지 확인
                        const previewImage = document.createElement("img");
                        previewImage.src = `data:image/png;base64,${data.attachment}`;
                        previewImage.classList.add("img-thumbnail");
                        previewImage.style.maxWidth = "100%";
                        previewContainer.appendChild(previewImage);
                    } else {
                        // 이미지가 아닌 경우 파일명과 다운로드 링크 표시
                        const fileLink = document.createElement("a");
                        fileLink.href = `data:application/octet-stream;base64,${data.attachment}`;
                        fileLink.download = data.attachment_filename;
                        fileLink.textContent = `${data.attachment_filename} 다운로드`;
                        previewContainer.appendChild(fileLink);
                    }

                    // content 상단에 미리보기 추가
                    contentElement.parentNode.insertBefore(previewContainer, contentElement);
                }

                // 글 목록 버튼의 링크를 qaType에 따라 설정
                const backToListButton = document.getElementById("backToListButton");
                backToListButton.addEventListener("click", function () {
                    if (qaType === "CUSTOMER") {
                        window.location.href = "/qa";
                    } else {
                        window.location.href = "/lost";
                    }
                });
            } else {
                alert("글을 불러오는 데 실패했습니다.");
            }
        } catch (error) {
            console.error("Error fetching QA:", error);
            alert("서버와 통신 중 문제가 발생했습니다.");
        }
    }
});
