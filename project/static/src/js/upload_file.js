
    document.querySelectorAll(".upload-trigger").forEach(btn => {
    btn.addEventListener("click", () => {
        const type = btn.getAttribute("data-type");
        const title = btn.getAttribute("data-title");
        const description = btn.getAttribute("data-description");

        document.getElementById("modalTitle").textContent = title;
        document.getElementById("modalDescription").textContent = description;
        document.getElementById("uploadAction").value = `upload_${type}`;

        const modal = document.getElementById("fileUploadModal");
        modal.classList.remove("hidden");
        modal.classList.add("opacity-100");
    });
    });
    document.getElementById("cancelFileUploadButton").addEventListener("click", () => {
    const modal = document.getElementById("fileUploadModal");
    modal.classList.add("hidden");
    modal.classList.remove("opacity-100");
    });
    document.getElementById("closeFileUploadModal").addEventListener("click", () => {
    const modal = document.getElementById("fileUploadModal");
    modal.classList.add("hidden");
    modal.classList.remove("opacity-100");
    });



