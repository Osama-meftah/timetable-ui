function showMessageModal(type, title, message) {
  const messageModal = document.getElementById("messageModal");
  const modalHeader = document.getElementById("modalHeader");
  const modalIcon = document.getElementById("modalIcon");
  const modalTitle = document.getElementById("modalTitle");
  const modalMessage = document.getElementById("modalMessage");

  if (
    !messageModal ||
    !modalHeader ||
    !modalIcon ||
    !modalTitle ||
    !modalMessage
  ) {
    console.error("Modal elements not found.");
    return;
  }

  modalHeader.className =
    "modal-header p-4 rounded-t-lg flex items-center justify-between";
  modalIcon.className = "text-xl ml-2";
  modalIcon.classList.remove(
    "fa-check-circle",
    "fa-times-circle",
    "fa-info-circle",
    "fa-exclamation-triangle"
  );

  if (type === "success") {
    modalHeader.classList.add("bg-green-500", "text-white");
    modalIcon.classList.add("fas", "fa-check-circle");
    modalTitle.textContent = title || "نجاح";
  } else if (type === "error") {
    modalHeader.classList.add("bg-red-600", "text-white");
    modalIcon.classList.add("fas", "fa-times-circle");
    modalTitle.textContent = title || "خطأ";
  } else if (type === "warning") {
    modalHeader.classList.add("bg-yellow-500", "text-white");
    modalIcon.classList.add("fas", "fa-exclamation-triangle");
    modalTitle.textContent = title || "تحذير";
  } else {
    modalHeader.classList.add("bg-blue-500", "text-white");
    modalIcon.classList.add("fas", "fa-info-circle");
    modalTitle.textContent = title || "رسالة";
  }

  modalMessage.textContent = message;
  messageModal.classList.add("show");
}

function hideMessageModal() {
  const messageModal = document.getElementById("messageModal");
  if (messageModal) {
    messageModal.classList.remove("show");
  }
}
