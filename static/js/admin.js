// static/js/dashboard.js

import {getToken} from './auth.js';

document.addEventListener("DOMContentLoaded", async () => {
    if (!getToken()) {
        window.location.href = '/adm/login';
        return;
    }

    // try {
    //     const response = await authFetch('/api/adm', {
    //         method: 'GET'
    //     });
    //     if (!response.ok) throw new Error("Data fetching failed");
    //
    //     const data = await response.json();
    // } catch (error) {
    //     console.error("Error loading data:", error);
    //     alert("데이터를 로드하는 중 문제가 발생했습니다.");
    // }
});

