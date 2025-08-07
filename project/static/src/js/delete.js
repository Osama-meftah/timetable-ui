let currentActionUrl = "";
const itemIdInput = document.getElementById("deleteItemIdInput");
const itemName = document.getElementById("modalItemName");
const itemType = document.getElementById("modalItemType");
const modal = document.getElementById("deleteGenericModal");
const modalContent = modal.querySelector(".max-w-lg");
const form = document.getElementById("deleteGenericForm");
const confirmBtn = document.getElementById("confirmDeleteBtn");

// 📌 دالة واحدة لإعداد الحذف وعرض المودال
function prepareDeleteModal(btn) {
  const id = btn.getAttribute("data-id");
  const name = btn.getAttribute("data-name");
  const type = btn.getAttribute("data-type");
  const formType = btn.getAttribute("data-form-type");
  const mainId = btn.getAttribute("data-main-id");
  let url;
  //  = btn.getAttribute("data-url").replace("0", id);
  if (mainId) {
    url = btn.getAttribute("data-url").replace("0", mainId);
  }
  else {
    url = btn.getAttribute("data-url").replace("0", id);
  }
  console.log(url);
  // const url = btn.getAttribute("data-url").replace("0", id);
  // const teacherIdInput =
  //   document.getElementById("selected_teacher_id")?.value || null;
  // const studentIdInput =
  //   document.getElementById("deleteItemIdInput")?.value || null;
  console.log(`Preparing to delete item with ID: ${id}, main id: ${mainId}, Type: ${type}, Form Type: ${formType}, URL: ${url}`);
  if (!id || !name || !type || !formType || !url) {
    showMessageModal(
      "error", // نوع الرسالة (error, success, warning, info)
      "خطأ في البيانات", // العنوان
      "الرجاء التأكد من وجود جميع القيم المطلوبة:\n- المعرف (id)\n- الاسم (name)\n- النوع (type)\n- نوع النموذج (formType)\n- الرابط (url)"
    );
    return;
  }

  // if (document.getElementById("selectedTeacherId")) {
  //   document.getElementById("selectedTeacherId").value = teacherIdInput;
  // }
  // console.log(`teacherIdInput: ${teacherIdInput}`);
  currentActionUrl = url;
  itemIdInput.value = id;
  itemName.textContent = name;
  itemType.textContent = type;
  document.getElementById("deleteFormTypeInput").value = formType;

  if (type === "program" || type === "level") {
    const selectedLevelOrProgram = document.getElementById(
      "selectedLevelOrProgram"
    );
    if (selectedLevelOrProgram) {
      selectedLevelOrProgram.value = type;
      console.log(selectedLevelOrProgram.value);
    }
  }

  console.log(`Preparing to delete ${type} with ID ${id}`);
  showModal();
}

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

document.addEventListener("DOMContentLoaded", function () {
  confirmBtn.addEventListener("click", () => {
    form.action = currentActionUrl;
    form.submit();
  });

  const closeButtons = modal.querySelectorAll(".close-modal-btn");
  closeButtons.forEach((btn) => btn.addEventListener("click", hideModal));

  modal.addEventListener("click", (e) => {
    if (e.target === modal) hideModal();
  });
});

// 🔁 مستمع عام واحد لجميع أزرار الحذف
document.addEventListener("click", function (event) {
  const btn = event.target.closest(".delete-btn");
  if (btn) {
    prepareDeleteModal(btn);
  }
});
