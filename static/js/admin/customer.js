import {authFetch} from "/static/js/auth.js";

const apiUrl = "/api/qas"; // API URL
const tableBody = document.getElementById("qa-table-body");
const loadingSpinner = document.getElementById("loading-spinner");
const filterSelect = document.querySelector(".form-select");

let allQAs = []; // 전체 데이터를 저장할 변수

// 로딩 스피너 표시/숨김 함수
const showSpinner = () => {
    loadingSpinner.style.setProperty("display", "flex", "important");
};

const hideSpinner = () => {
    loadingSpinner.style.setProperty("display", "none", "important");
};

// 데이터 렌더링 함수
const renderQAs = (filter = "all") => {
    let filteredQAs;

    if (filter === "0") {
        filteredQAs = allQAs.filter((qa) => qa.done === false); // 처리중 데이터만
    } else if (filter === "1") {
        filteredQAs = allQAs.filter((qa) => qa.done === true); // 답변완료 데이터만
    } else {
        filteredQAs = allQAs; // 전체 데이터
    }

    tableBody.innerHTML = filteredQAs
        .map(
            (qa) => `
            <tr data-id="${qa.id}">
                <td>${qa.num}</td>
                <td>${qa.title}</td>
                <td class="text-center">${qa.c_date}</td>
                <td class="text-center">${qa.done ? "완료" : "진행 중"}</td>
                <td class="text-center">${qa.read_cnt}</td>
            </tr>
        `
        )
        .join("");

    if (filteredQAs.length === 0) {
        tableBody.innerHTML = `<tr><td colspan="4" class="text-center">데이터가 없습니다.</td></tr>`;
    }
};

// 데이터 가져오기
const fetchQAs = async () => {
    try {
        showSpinner();
        const response = await authFetch(`${apiUrl}?qa_type=CUSTOMER`);
        const data = await response.json();

        allQAs = data.qas; // 전체 데이터를 저장
        renderQAs("all"); // 초기 전체 데이터 렌더링
    } catch (error) {
        console.error("Error fetching QAs:", error);
    } finally {
        hideSpinner();
    }
};

// 셀렉트 박스 변경 이벤트 핸들러
filterSelect.addEventListener("change", () => {
    const selectedValue = filterSelect.value; // 선택된 값 가져오기

    if (selectedValue === "all") {
        renderQAs("all");
    } else if (selectedValue === "0") {
        renderQAs("0"); // 처리중 보기
    } else if (selectedValue === "1") {
        renderQAs("1"); // 답변완료 보기
    }
});

// Initialize the app
document.addEventListener("DOMContentLoaded", () => {
    fetchQAs(); // 기본적으로 전체 데이터 가져오기
});
