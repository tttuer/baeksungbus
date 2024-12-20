import {authFetch} from "/static/js/auth.js";

document.addEventListener("DOMContentLoaded", () => {
    const apiUrl = "/api/ddocks"; // API URL
    const tableBody = document.getElementById("ddock-table-body");
    const preview = document.getElementById("image-preview");
    const previewImg = document.getElementById("preview-img");
    const submitButton = document.getElementById("submit-schedule-btn");

    // Fetch and render ddocks data
    const fetchDdocks = async () => {
        try {
            const response = await authFetch(apiUrl);
            const data = await response.json();
            const ddocks = data.ddocks;

            tableBody.innerHTML = ""; // Clear table body

            ddocks.forEach((item, index) => {
                const row = document.createElement("tr");

                // 번호
                const numberCell = document.createElement("td");
                numberCell.textContent = index + 1;
                row.appendChild(numberCell);

                // 제목
                const titleCell = document.createElement("td");
                const titleLink = document.createElement("span");
                titleLink.textContent = item.image_name;
                titleLink.style.cursor = "pointer";
                titleLink.addEventListener("mouseover", (event) => {
                    if (item.image) {
                        previewImg.src = `data:image/png;base64,${item.image}`;
                        preview.style.display = "block";
                        preview.style.top = `${event.clientY + 10}px`;
                        preview.style.left = `${event.clientX + 10}px`;
                    }
                });
                titleLink.addEventListener("mouseout", () => {
                    preview.style.display = "none";
                });
                titleCell.appendChild(titleLink);
                row.appendChild(titleCell);

                // 수정 버튼
                const editCell = document.createElement("td");
                editCell.classList.add("text-center");
                const editButton = document.createElement("button");
                editButton.textContent = "수정";
                editButton.classList.add("btn", "btn-primary", "btn-sm");
                editCell.appendChild(editButton);
                row.appendChild(editCell);

                // 삭제 버튼
                const deleteCell = document.createElement("td");
                deleteCell.classList.add("text-center");
                const deleteButton = document.createElement("button");
                deleteButton.textContent = "삭제";
                deleteButton.classList.add("btn", "btn-danger", "btn-sm");
                deleteCell.appendChild(deleteButton);
                row.appendChild(deleteCell);

                tableBody.appendChild(row);
            });
        } catch (error) {
            console.error("Error fetching ddocks:", error);
        }
    };

    // Upload images
    submitButton.addEventListener("click", async () => {
        const inputElement = document.getElementById("imageUpload");
        const files = inputElement.files; // Selected files
        const formData = new FormData();

        // Append files to FormData
        for (let i = 0; i < files.length; i++) {
            formData.append("images", files[i]);
        }

        try {
            const response = await authFetch(apiUrl, {
                method: "POST",
                body: formData,
            });

            if (response.ok) {
                alert("Images uploaded successfully!");
                // Close modal
                const modal = document.getElementById("scheduleModal");
                const modalInstance = bootstrap.Modal.getInstance(modal);
                modalInstance.hide();

                // Refresh ddocks data
                await fetchDdocks();
            } else {
                alert("Failed to upload images.");
            }
        } catch (err) {
            console.error("Error uploading images:", err);
            alert("An error occurred during upload.");
        }
    });

    // Initialize ddocks data on page load
    fetchDdocks();

    // Update preview position dynamically
    document.addEventListener("mousemove", (event) => {
        if (preview.style.display === "block") {
            preview.style.top = `${event.clientY + 10}px`;
            preview.style.left = `${event.clientX + 10}px`;
        }
    });
});
