import {authFetch} from "/static/js/auth.js";

const apiUrl = "/api/ddocks"; // API URL
const tableBody = document.getElementById("ddock-table-body");
const preview = document.getElementById("image-preview");
const previewImg = document.getElementById("preview-img");
let attachedFile = null; // 단일 첨부파일을 저장하는 변수
let draggedRow = null; // 드래그 중인 행
// 로딩 스피너 엘리먼트 가져오기
const loadingSpinner = document.getElementById("loading-spinner");

const showSpinner = () => {
    loadingSpinner.style.setProperty("display", "flex", "important");
};

const hideSpinner = () => {
    loadingSpinner.style.setProperty("display", "none", "important");
};

// Fetch and render ddocks data
const fetchDdocks = async () => {
    try {
        // 로딩 스피너 표시
        showSpinner()
        const response = await authFetch(apiUrl);
        const data = await response.json();
        const ddocks = data.ddocks;

        tableBody.innerHTML = ddocks
            .map(
                (item, index) => `
                <tr draggable="true" data-id="${item.id}" data-order="${item.order}">
                    <td>${index + 1}</td>
                    <td>
                        <span class="title-link" style="cursor: pointer;" data-id="${item.id}" data-image="${item.image}">
                            ${item.image_name || "첨부파일 없음"}
                        </span>
                    </td>
                    <td class="text-center">
                        <button class="btn btn-sm btn-primary edit-btn" data-id="${item.id}">수정</button>
                    </td>
                    <td class="text-center">
                        <button class="btn btn-sm btn-danger delete-btn" data-id="${item.id}">삭제</button>
                    </td>
                </tr>
            `
            )
            .join("");

        // Attach events
        attachEditDeleteEvents();
        attachPreviewEvents();
        attachDragAndDropEvents(); // 드래그앤드랍 이벤트 추가
    } catch (error) {
        console.error("Error fetching ddocks:", error);
    } finally {
        hideSpinner()
    }
};

// Attach drag and drop events
const attachDragAndDropEvents = () => {
    const rows = tableBody.querySelectorAll("tr");

    rows.forEach((row) => {
        row.addEventListener("dragstart", (e) => {
            draggedRow = e.target; // 드래그 중인 행 설정
            e.target.style.opacity = 0.5;
        });

        row.addEventListener("dragover", (e) => {
            e.preventDefault(); // 기본 동작 방지 (드롭 가능하도록 설정)
        });

        row.addEventListener("drop", (e) => {
            e.preventDefault();

            if (draggedRow && draggedRow !== e.target) {
                const targetRow = e.target.closest("tr");
                tableBody.insertBefore(draggedRow, targetRow.nextSibling);

                // 순서 갱신
                updateOrder();
            }
        });

        row.addEventListener("dragend", (e) => {
            e.target.style.opacity = 1;
            draggedRow = null; // 드래그 상태 초기화
        });
    });
};

// Update order based on table row positions
const updateOrder = () => {
    const rows = tableBody.querySelectorAll("tr");
    const updatedOrder = Array.from(rows).map((row, index) => ({
        id: row.getAttribute("data-id"),
        order: index + 1, // 순서 업데이트
    }));


    // 서버에 업데이트 요청
    updateOrderOnServer(updatedOrder);
};

// Send updated order to server
const updateOrderOnServer = async (updatedOrder) => {
    try {
        const response = await authFetch(`${apiUrl}/order`, {
            method: "PATCH",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({orders: updatedOrder}),
        });

        if (response.ok) {
            alert("순서가 성공적으로 업데이트되었습니다.");
        } else {
            throw new Error("Order update failed.");
        }
    } catch (error) {
        console.error("Error updating order:", error);
        alert("순서 업데이트에 실패했습니다.");
    }
};

// Attach events for edit and delete buttons
const attachEditDeleteEvents = () => {
    document.querySelectorAll(".edit-btn").forEach((button) => {
        button.addEventListener("click", (e) => {
            const ddockId = e.target.getAttribute("data-id");
            editDdock(ddockId);
        });
    });

    document.querySelectorAll(".delete-btn").forEach((button) => {
        button.addEventListener("click", (e) => {
            const ddockId = e.target.getAttribute("data-id");
            deleteDdock(ddockId);
        });
    });
};

// Attach preview events for title links
const attachPreviewEvents = () => {
    document.querySelectorAll(".title-link").forEach((link) => {
        link.addEventListener("mouseover", (event) => {
            const image = link.getAttribute("data-image");
            if (image) {
                previewImg.src = `data:image/png;base64,${image}`;
                preview.style.display = "block";
                preview.style.top = `${event.clientY + 10}px`;
                preview.style.left = `${event.clientX + 10}px`;
            }
        });

        link.addEventListener("mouseout", () => {
            preview.style.display = "none";
        });
    });
};

// Edit ddock
const editDdock = (id) => {
    resetEditModal();
    authFetch(`/api/ddocks/${id}`)
        .then((response) => response.json())
        .then((ddock) => {
            document.getElementById("editId").value = ddock.id;
            attachedFile = ddock.image_name
                ? {name: ddock.image_name, data: ddock.image}
                : null;

            renderAttachment();

            const modal = new bootstrap.Modal(document.getElementById("editDdockModal"));
            modal.show();
        })
        .catch((error) => console.error("Error loading ddock:", error));
};

// Delete ddock
const deleteDdock = async (id) => {
    if (confirm("정말로 삭제하시겠습니까?")) {
        try {
            const response = await authFetch(`${apiUrl}/${id}`, {
                method: "DELETE",
            });
            if (response.ok) {
                alert("삭제에 성공했습니다.");
                await fetchDdocks();
            } else {
                alert("Failed to delete ddock.");
            }
        } catch (error) {
            console.error("Error deleting ddock:", error);
        }
    }
};

// Reset and render attachment UI
const resetEditModal = () => {
    document.getElementById("editId").value = "";
    attachedFile = null;
    renderAttachment();
};

const renderAttachment = () => {
    const fileContainer = document.getElementById("editAttachments");
    fileContainer.innerHTML = attachedFile
        ? `
        <div class="d-flex align-items-center mb-2">
            <span>첨부파일: ${attachedFile.name}</span>
            <button type="button" class="btn btn-sm btn-outline-danger ms-2" onclick="removeFile()">삭제</button>
        </div>
    `
        : `<span>첨부파일 없음</span>`;
};

// Remove file from attachments
window.removeFile = function () {
    attachedFile = null;
    renderAttachment();
};

// Upload images
const submitDdockForm = async () => {
    const inputElement = document.getElementById("imageUpload");
    const files = inputElement.files;
    const formData = new FormData();

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
            const modal = bootstrap.Modal.getInstance(document.getElementById("scheduleModal"));
            modal.hide();
            await fetchDdocks();
        } else {
            alert("Failed to upload images.");
        }
    } catch (error) {
        console.error("Error uploading images:", error);
    }
};

// Save edited ddock
const saveEditedDdock = async () => {
    const id = document.getElementById("editId").value;
    const formData = new FormData();

    const newFileInput = document.querySelector(".new-file-input");

    // If no file exists and no new file is uploaded, delete the file
    if (!attachedFile && !newFileInput.files.length) {
        await deleteFile(id);
        alert("파일이 삭제되었습니다.");
        fetchDdocks();
        const modal = bootstrap.Modal.getInstance(document.getElementById("editDdockModal"));
        modal.hide();
        return;
    }

    // Add new file if provided
    if (newFileInput.files[0]) {
        formData.append("image", newFileInput.files[0]);
    } else if (attachedFile) {
        formData.append("image_name", attachedFile.name);
    }

    authFetch(`/api/ddocks/${id}`, {
        method: "PUT",
        body: formData,
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error("Update failed");
            }
            alert("수정 완료!");
            fetchDdocks();
            const modal = bootstrap.Modal.getInstance(document.getElementById("editDdockModal"));
            modal.hide();
        })
        .catch((error) => console.error("Error:", error));
};

// Delete file from server
const deleteFile = async (id) => {
    try {
        const response = await authFetch(`${apiUrl}/${id}`, {method: "DELETE"});
        if (!response.ok) {
            throw new Error("Failed to delete file");
        }
    } catch (error) {
        console.error("Error deleting file:", error);
    }
};

// Initialize the app
document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("submit-schedule-btn").addEventListener("click", submitDdockForm);
    document.getElementById("save-edit-btn").addEventListener("click", saveEditedDdock);
    fetchDdocks();
});
