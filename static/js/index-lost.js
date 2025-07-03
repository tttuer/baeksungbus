document.addEventListener("DOMContentLoaded", async () => {
    const qaList = document.getElementById("qa-list");
    const passwordModal = new bootstrap.Modal(document.getElementById("password-modal"));
    const passwordInput = document.getElementById("qa-password"); // 비밀번호 입력 필드
    const divider = document.querySelector(".featurette-divider"); // 구분선 요소
    let currentQaId = null;
    let isHidden = false; // 현재 클릭한 QA의 숨김 여부

    // 구분선 위치 조정 함수
    const adjustDividerPosition = () => {
        const listHeight = qaList.offsetHeight; // 리스트 높이 계산
        const baseHeight = 180; // 기본 높이
        const extraMargin = 20; // 추가 간격

        if (listHeight > baseHeight) {
            divider.style.marginTop = `${listHeight - baseHeight + extraMargin}px`;
        } else {
            divider.style.marginTop = "20px"; // 기본 간격
        }
    };

    // QA 리스트 렌더링
    try {
        const response = await fetch("/api/qas?qa_type=LOST&page=1&page_size=5");
        const data = await response.json();

        if (response.ok && data.qas) {
            data.qas.forEach((qa) => {
                const listItem = document.createElement("li");
                listItem.className = "list-group-item";
                listItem.innerHTML = `
                    <a href="#" class="qa-link text-decoration-none" data-id="${qa.id}" data-hidden="${qa.hidden}">
                        ${qa.title}${qa.hidden ? '<i class="bi bi-file-lock ms-2" title="비공개 글"></i>' : ''}
                    </a>
                `;
                qaList.appendChild(listItem);
            });

            // 리스트 렌더링 후 구분선 위치 조정
            adjustDividerPosition();
        } else {
            qaList.innerHTML = "<li class='list-group-item'>항목을 불러오는 데 실패했습니다.</li>";
        }
    } catch (error) {
        console.error("Error fetching QAs:", error);
        qaList.innerHTML = "<li class='list-group-item'>오류가 발생했습니다.</li>";
    }

    // 클릭 이벤트 처리
    qaList.addEventListener("click", async (event) => {
        if (event.target.matches(".qa-link")) {
            event.preventDefault();
            const qaId = event.target.getAttribute("data-id");
            isHidden = event.target.getAttribute("data-hidden") === "true"; // 숨김 여부 확인
            currentQaId = qaId;

            if (isHidden) {
                passwordInput.value = "";

                // 비공개 글일 경우 비밀번호 입력 모달 표시
                passwordModal.show();
            } else {
                // 공개 글일 경우 바로 상세화면으로 이동
                window.location.href = `/qa/detail?id=${qaId}`;
            }
        }
    });

    // 비밀번호 제출 이벤트
    document.getElementById("submit-password").addEventListener("click", async () => {
        const password = document.getElementById("qa-password").value;

        try {
            const response = await fetch(`/api/qas/${currentQaId}/check_password?password=${encodeURIComponent(password)}`);

            if (response.ok) {
                // 비밀번호가 맞으면 상세화면으로 이동
                window.location.href = `/qa/detail?id=${currentQaId}`;
            } else {
                alert("비밀번호가 올바르지 않습니다.");
            }
        } catch (error) {
            console.error("Error verifying password:", error);
            alert("오류가 발생했습니다.");
        }
    });
});
