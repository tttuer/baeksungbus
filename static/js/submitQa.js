async function handleSubmit(event) {
    event.preventDefault();

    const formElement = document.getElementById("qaForm");
    const formData = new FormData(formElement);

    // 빈 값 제거
    for (const [key, value] of formData.entries()) {
        if (!value) {
            formData.delete(key);
        }
    }

    try {
        const response = await fetch("/api/qas", {
            method: "POST",
            body: formData,
        });

        if (response.ok) {
            alert("글이 성공적으로 작성되었습니다!");
            window.location.href = "/qa";  // 성공 시 /qa로 리디렉션
        } else {
            const errorData = await response.json();
            alert("글 작성에 실패했습니다: " + errorData.detail);
        }
    } catch (error) {
        console.error("Error:", error);
        alert("서버와 통신 중 문제가 발생했습니다.");
    }
}
