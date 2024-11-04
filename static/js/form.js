document.addEventListener("DOMContentLoaded", function () {
    const quill = new Quill('#editor', {
        theme: 'snow'
    });

    document.getElementById('submissionForm').addEventListener("submit", handleSubmit);

    async function handleSubmit(event) {
        event.preventDefault(); // 폼 기본 제출 방지

        // CAPTCHA 입력 값 가져오기
        const captchaInput = document.getElementById('captcha').value;

        try {
            // CAPTCHA 인증 요청
            const response = await fetch('/submit', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: new URLSearchParams({captcha: captchaInput})
            });

            if (response.ok) {
                // CAPTCHA 인증 성공 시 전체 폼 데이터를 전송
                const formData = new FormData(document.getElementById('submissionForm'));

                // Quill 에디터 내용 추가
                formData.append("content", quill.root.innerHTML);

                // 실제 폼 데이터 전송
                const submitResponse = await fetch('/submit', {
                    method: 'POST',
                    body: formData
                });

                if (submitResponse.ok) {
                    alert("폼이 성공적으로 제출되었습니다.");
                } else {
                    alert("폼 제출에 실패했습니다.");
                }
            } else {
                // CAPTCHA 인증 실패 시 에러 표시
                alert("자동등록방지 문자가 올바르지 않습니다.");
            }
        } catch (error) {
            console.error("Error during CAPTCHA validation:", error);
            alert("서버 오류가 발생했습니다. 다시 시도해주세요.");
        }
    }

    // CAPTCHA 새로고침 함수
    function refreshCaptcha() {
        const captchaImage = document.getElementById("captchaImage");
        captchaImage.src = `/captcha_image?${new Date().getTime()}`; // 새 이미지 로드
    }

    document.getElementById('refreshCaptcha').addEventListener("click", refreshCaptcha);
});
