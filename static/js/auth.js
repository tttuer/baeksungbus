// static/js/auth.js

export function saveToken(token) {
    localStorage.setItem('access_token', token);
}

export function getToken() {
    return localStorage.getItem('access_token');
}

export async function authFetch(url, options = {}) {
    const token = getToken();
    if (token) {
        options.headers = {
            ...options.headers,
            Authorization: `Bearer ${token}`,
        };
    }
    return fetch(url, options);
}

document.addEventListener("DOMContentLoaded", () => {
    // 로그인 초기화 코드
    const loginForm = document.querySelector("form");
    if (loginForm) {
        loginForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            const formData = new FormData(loginForm);
            try {
                const response = await fetch('/api/users/login', {
                    method: 'POST',
                    body: formData
                });
                if (response.ok) {
                    const data = await response.json();
                    saveToken(data.access_token);
                    window.location.href = '/adm';
                } else {
                    alert("로그인 실패: 잘못된 아이디 또는 비밀번호");
                }
            } catch (error) {
                console.error("로그인 중 오류 발생:", error);
            }
        });
    }
});
