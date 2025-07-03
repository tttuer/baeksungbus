// static/js/logout.js

document.addEventListener("DOMContentLoaded", () => {
    const logoutLink = document.getElementById("logout-link");

    if (logoutLink) {
        logoutLink.addEventListener("click", async (event) => {
            event.preventDefault(); // 기본 링크 동작 방지
            try {
                const response = await fetch('/api/users/logout', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'}
                });
                if (response.ok) {
                    localStorage.removeItem('access_token');
                    alert("로그아웃되었습니다.");
                    window.location.href = '/adm/login'; // 로그인 페이지로 이동
                } else {
                    alert("로그아웃에 실패했습니다.");
                }
            } catch (error) {
                console.error("로그아웃 중 오류 발생:", error);
            }
        });
    } else {
        console.error("로그아웃 링크를 찾을 수 없습니다.");
    }
});
