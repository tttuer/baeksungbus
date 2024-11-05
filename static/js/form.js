document.addEventListener("DOMContentLoaded", function () {
    'use strict';

    const quill = new Quill('#editor', {theme: 'snow'});
    const forms = document.querySelectorAll('.needs-validation');
    const captchaInput = document.getElementById("captcha");
    const captchaFeedback = document.querySelector(".captcha"); // 정확히 지정
    const captchaImage = document.getElementById("captchaImage");
    const refreshCaptchaButton = document.getElementById("refreshCaptcha");

    // CAPTCHA 새로고침 기능
    refreshCaptchaButton.addEventListener("click", function () {
        captchaImage.src = `/captcha_image?${new Date().getTime()}`;
    });

    Array.from(forms).forEach(form => {
        form.addEventListener('submit', async event => {
            event.preventDefault();

            // 기본 Bootstrap 유효성 검사를 수행
            if (!form.checkValidity()) {
                event.stopPropagation();
                form.classList.add('was-validated');
                return;
            }

            // CAPTCHA 검증 API 호출
            const captchaValue = captchaInput.value;
            const captchaResponse = await fetch("/submit", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: new URLSearchParams({captcha: captchaValue}),
            });

            // CAPTCHA 검증 결과 처리
            if (captchaResponse.ok) {
                // CAPTCHA 성공 시 전체 폼 데이터 전송
                const formData = new FormData(form);

                // Quill 에디터 내용 추가
                formData.append("content", quill.root.innerHTML);

                // 실제 폼 데이터 전송
                const submitResponse = await fetch('/api/qas/', {
                    method: 'POST',
                    body: formData
                });

                if (submitResponse.ok) {
                    // qa_type 값에 따라 리디렉션 결정
                    const qaType = formData.get("qa_type");
                    const redirectUrl = qaType === "CUSTOMER" ? "/qa" : "/lost";
                    window.location.href = redirectUrl; // 성공 시 해당 URL로 이동
                }
            } else {
                // CAPTCHA 실패 시 오류 표시
                captchaInput.classList.add("is-invalid");
                captchaFeedback.classList.add("d-block");
                captchaFeedback.textContent = "자동등록방지 문자가 올바르지 않습니다. 다시 입력해주세요.";
                captchaInput.value = "";  // 입력 초기화
                captchaImage.src = `/captcha_image?${new Date().getTime()}`;  // CAPTCHA 이미지 새로고침
                form.classList.add('was-validated');
            }
        });
    });
});
