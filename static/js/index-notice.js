document.addEventListener("DOMContentLoaded", async () => {
    const qaList = document.getElementById("notice-list");
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
        const response = await fetch("/api/notices?notice_type=NOTICE&page=1&page_size=5");
        const data = await response.json();

        if (response.ok && data.notices) {
            data.notices.forEach((notice) => {
                const listItem = document.createElement("li");
                listItem.className = "list-group-item";
                listItem.innerHTML = `
                    <a href="#" class="notice-link text-decoration-none" data-id="${notice.id}">
                        ${notice.title}
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
        if (event.target.matches(".notice-link")) {
            event.preventDefault();
            const qaId = event.target.getAttribute("data-id");
            isHidden = event.target.getAttribute("data-hidden") === "true"; // 숨김 여부 확인
            currentQaId = qaId;

            window.location.href = `/notices/detail?id=${qaId}`;

        }
    });
});
