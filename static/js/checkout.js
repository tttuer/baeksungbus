(() => {
  'use strict'

  const forms = document.querySelectorAll('.needs-validation')
  const captchaInput = document.getElementById("captcha")
  const captchaFeedback = captchaInput.nextElementSibling.nextElementSibling  // invalid-feedback 요소 선택 수정
  const captchaImage = document.getElementById("captchaImage")
  const refreshCaptchaButton = document.getElementById("refreshCaptcha")

  // CAPTCHA 새로고침 기능
  refreshCaptchaButton.addEventListener("click", function () {
    captchaImage.src = `/captcha_image?${new Date().getTime()}`
  })

  Array.from(forms).forEach(form => {
    form.addEventListener('submit', async event => {
      event.preventDefault()

      // 기본 Bootstrap 유효성 검사를 수행
      if (!form.checkValidity()) {
        event.stopPropagation()
        form.classList.add('was-validated')
        return
      }

      // CAPTCHA 검증 API 호출
      const captchaValue = captchaInput.value
      const response = await fetch("/submit", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({ captcha: captchaValue }),
      })

      // CAPTCHA 검증 결과 처리
      if (response.ok) {
        // CAPTCHA가 성공적으로 검증되면 is-invalid 제거 및 폼 제출
        captchaInput.classList.remove("is-invalid")
        captchaFeedback.style.display = "none"  // 오류 메시지 숨김
        form.submit()
      } else {
        // CAPTCHA가 잘못된 경우 invalid-feedback 표시
        captchaInput.classList.add("is-invalid")
        captchaFeedback.style.display = "block"
        captchaFeedback.textContent = "자동등록방지 문자가 올바르지 않습니다. 다시 입력해주세요."
        captchaInput.value = ""  // 입력 초기화
        captchaImage.src = `/captcha_image?${new Date().getTime()}`  // CAPTCHA 이미지 새로고침
        form.classList.add('was-validated')
      }
    }, false)
  })
})()
