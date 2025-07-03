// // static/js/login.js
//
// import {saveToken} from './auth.js';
//
// document.addEventListener("DOMContentLoaded", () => {
//     const loginForm = document.querySelector("form");
//
//     loginForm.addEventListener("submit", async (event) => {
//         event.preventDefault();
//
//         const formData = new FormData(loginForm);
//
//         try {
//             const response = await fetch('/api/users/login', {
//                 method: 'POST',
//                 body: formData
//             });
//
//             if (response.ok) {
//                 const data = await response.json();
//                 saveToken(data.access_token);  // 토큰 저장
//                 window.location.href = '/adm'; // 로그인 성공 시 리다이렉트
//             } else {
//                 alert("로그인 실패: 잘못된 아이디 또는 비밀번호");
//             }
//         } catch (error) {
//             console.error("로그인 중 오류 발생:", error);
//         }
//     });
// });
