document.addEventListener("DOMContentLoaded", function () {
    const quill = new Quill('#editor', {
        theme: 'snow'
    });

    document.querySelector("form").addEventListener("submit", function (event) {
        event.preventDefault();

        // 에디터 내용을 HTML로 가져와 숨겨진 input에 저장
        const contentInput = document.createElement("input");
        contentInput.type = "hidden";
        contentInput.name = "content";
        contentInput.value = quill.root.innerHTML; // Quill의 HTML 내용을 가져옴
        this.appendChild(contentInput);

        this.submit();
    });
});
