document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".upload-trigger").forEach((btn) => {
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

  const cancelBtn = document.getElementById("cancelFileUploadButton");
  if (cancelBtn) {
    cancelBtn.addEventListener("click", () => {
      const modal = document.getElementById("fileUploadModal");
      modal.classList.add("hidden");
      modal.classList.remove("opacity-100");
    });
  }

  const closeBtn = document.getElementById("closeFileUploadModal");
  if (closeBtn) {
    closeBtn.addEventListener("click", () => {
      const modal = document.getElementById("fileUploadModal");
      modal.classList.add("hidden");
      modal.classList.remove("opacity-100");
    });
  }
});
