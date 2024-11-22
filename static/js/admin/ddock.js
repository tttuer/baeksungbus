import {authFetch} from "../auth";

document.addEventListener("DOMContentLoaded", () => {
    const submitButton = document.getElementById("submit-schedule-btn");

    submitButton.addEventListener("click", async () => {
        const inputElement = document.getElementById("imageUpload");
        const files = inputElement.files; // 선택된 파일들 가져오기
        const formData = new FormData();

        // FormData에 파일 추가
        for (let i = 0; i < files.length; i++) {
            formData.append("images", files[i]);
        }

        try {
            // POST 요청 보내기
            const response = await authFetch("/ddock", {
                method: "POST",
                body: formData,
            });

            if (response.ok) {
                alert("Images uploaded successfully!");
                // 모달 닫기
                const modal = document.getElementById("scheduleModal");
                const modalInstance = bootstrap.Modal.getInstance(modal);
                modalInstance.hide();
            } else {
                alert("Failed to upload images.");
            }
        } catch (err) {
            console.error("Error uploading images:", err);
            alert("An error occurred during upload.");
        }
    });
});
