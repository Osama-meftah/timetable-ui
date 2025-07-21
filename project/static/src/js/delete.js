let currentActionUrl = "";
const itemIdInput = document.getElementById("deleteItemIdInput");
const itemName = document.getElementById("modalItemName");
const itemType = document.getElementById("modalItemType");

document.addEventListener("DOMContentLoaded", function () {
  const modal = document.getElementById("deleteGenericModal");
  const modalContent = modal.querySelector(".max-w-lg");
  const form = document.getElementById("deleteGenericForm");
  const confirmBtn = document.getElementById("confirmDeleteBtn");
  const closeButtons = modal.querySelectorAll(".close-modal-btn");

  document.querySelectorAll(".delete-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const id = btn.getAttribute("data-id");
      const name = btn.getAttribute("data-name");
      const type = btn.getAttribute("data-type");
      const formType = btn.getAttribute("data-form-type");
      const url = btn.getAttribute("data-url").replace("0", id);
      const teacherIdInput =
        document.getElementById("selected_teachers_id")?.value || null;
      if (selectedTeacherId) {
        const selectedTeacherId = document.getElementById("selectedTeacherId");
        selectedTeacherId.value = teacherIdInput;
      }

      currentActionUrl = url;
      itemIdInput.value = id;
      itemName.textContent = name;
      itemType.textContent = type;

      if (type === "program" || type === "level") {
        selectedLevelOrProgram = document.getElementById(
          "selectedLevelOrProgram"
        );
        selectedLevelOrProgram.value = type;
        console.log(selectedLevelOrProgram.value);
      }
      document.getElementById("deleteFormTypeInput").value = formType;

      console.log(`Preparing to delete ${type} with ID ${id}`);

      showModal();
    });
  });

  confirmBtn.addEventListener("click", () => {
    form.action = currentActionUrl;
    form.submit();
  });

  closeButtons.forEach((btn) => btn.addEventListener("click", hideModal));
  modal.addEventListener("click", (e) => {
    if (e.target === modal) hideModal();
  });

  function showModal() {
    modal.classList.remove("opacity-0", "invisible");
    modal.classList.add("opacity-100", "visible");
    modalContent.classList.remove("scale-95", "opacity-0");
    modalContent.classList.add("scale-100", "opacity-100");
  }

  function hideModal() {
    modalContent.classList.remove("scale-100", "opacity-100");
    modalContent.classList.add("scale-95", "opacity-0");
    modalContent.addEventListener(
      "transitionend",
      function handler() {
        modal.classList.remove("opacity-100", "visible");
        modal.classList.add("opacity-0", "invisible");
        modalContent.removeEventListener("transitionend", handler);
      },
      { once: true }
    );
  }
});

// *** الإضافة المهمة: مستمع عام لأزرار الحذف يعمل مع كل الأزرار القديمة والجديدة ***
document.addEventListener("click", function (event) {
  const btn = event.target.closest(".delete-btn");
  if (!btn) return;

  const id = btn.getAttribute("data-id");
  const name = btn.getAttribute("data-name");
  const type = btn.getAttribute("data-type");
  const formType = btn.getAttribute("data-form-type");
  const url = btn.getAttribute("data-url").replace("0", id);

  currentActionUrl = url;
  itemIdInput.value = id;
  itemName.textContent = name;
  itemType.textContent = type;
  document.getElementById("deleteFormTypeInput").value = formType;

  console.log(`Preparing to delete ${type} with ID ${id}`);

  const modal = document.getElementById("deleteGenericModal");
  const modalContent = modal.querySelector(".max-w-lg");

  function showModal() {
    modal.classList.remove("opacity-0", "invisible");
    modal.classList.add("opacity-100", "visible");
    modalContent.classList.remove("scale-95", "opacity-0");
    modalContent.classList.add("scale-100", "opacity-100");
  }

  showModal();
});
