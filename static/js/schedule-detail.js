// schedule-detail.js

// Helper to get query parameters
function getQueryParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

// Fetch and display schedule details
function loadScheduleDetail() {
    const scheduleId = getQueryParam('id');
    if (!scheduleId) {
        console.error('No schedule ID found in URL');
        return;
    }

    fetch(`/api/schedules/${scheduleId}`)
        .then(response => response.json())
        .then(schedule => {
            // Populate title
            document.getElementById('title').value = schedule.title;

            // Display images if available
            const contentDiv = document.getElementById('editor');
            contentDiv.innerHTML = ''; // Clear content

            const attachmentSection = document.getElementById('attachmentSection');
            const attachmentPreviewContainer = document.getElementById('attachmentPreviewContainer');
            attachmentPreviewContainer.innerHTML = ''; // Clear previous attachments

            const images = [
                {data: schedule.image_data1, name: schedule.image_name1},
                {data: schedule.image_data2, name: schedule.image_name2},
                {data: schedule.image_data3, name: schedule.image_name3}
            ];
            images.forEach((image, index) => {
                if (image.data) {

                    const imgElement = document.createElement('img');
                    imgElement.src = `data:image/png;base64,${image.data}`;
                    imgElement.classList.add('d-block', 'mb-3');
                    imgElement.style.maxWidth = '100%';

                    imgElement.style.cursor = 'pointer';


                    // 이미지 클릭 이벤트 추가
                    imgElement.addEventListener('click', () => {
                        const newWindow = window.open();
                        newWindow.document.write(`
                <html>
                <head><title>${image.name}</title></head>
                <body style="display: flex; justify-content: center; align-items: center; margin: 0;">
                    <img src="data:image/png;base64,${image.data}" style="max-width: 100%; max-height: 100vh;">
                </body>
                </html>
            `);
                    });

                    contentDiv.appendChild(imgElement);

                    const downloadLink = document.createElement('a');
                    downloadLink.href = `data:application/octet-stream;base64,${image.data}`;
                    downloadLink.download = image.name || `attachment${index + 1}`;
                    downloadLink.textContent = `${downloadLink.download} 다운로드`;
                    downloadLink.style.display = 'block';
                    downloadLink.style.marginTop = '10px';

                    attachmentPreviewContainer.appendChild(downloadLink);
                }
            });
        })
        .catch(error => console.error('Error loading schedule details:', error));
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadScheduleDetail();

    // '글 목록' 버튼 클릭 시 /schedule로 이동
    const backToListButton = document.getElementById('backToListButton');
    if (backToListButton) {
        backToListButton.addEventListener('click', () => {
            window.location.href = '/schedule';
        });
    }
});
