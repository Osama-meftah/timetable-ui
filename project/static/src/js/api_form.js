class APIFormManager {
  constructor({
    formId,
    listContainerId,
    apiBaseUrl,
    renderItem,
    getFormData,
  }) {
    this.form = document.getElementById(formId);
    this.listContainer = document.getElementById(listContainerId);
    this.apiBaseUrl = apiBaseUrl;
    this.renderItem = renderItem;
    this.getFormData = getFormData;
    this.csrfToken = document.querySelector(
      'input[name="csrfmiddlewaretoken"]'
    )?.value;

    this.init();
  }

  init() {
    this.fetchItems();

    if (this.form) {
      this.form.addEventListener("submit", (e) => {
        e.preventDefault();
        this.handleSubmit();
      });
    }

    // Listen for global delete clicks
    this.listContainer.addEventListener("click", (e) => {
      if (e.target.closest(".delete-btn")) {
        const id = e.target.closest(".delete-btn").dataset.id;
        this.handleDelete(id);
      }
    });
  }

  async fetchItems() {
    try {
      const res = await fetch(this.apiBaseUrl);
      if (!res.ok) throw new Error("Failed to fetch items.");
      const data = await res.json();
      this.renderList(data);
    } catch (error) {
      console.error(error);
      this.showCustomAlert("فشل تحميل البيانات.", "error");
    }
  }

  renderList(items) {
    this.listContainer.innerHTML = "";
    if (!items.length) {
      this.listContainer.innerHTML =
        '<p class="text-gray-500 dark:text-gray-300">لا توجد بيانات.</p>';
      return;
    }

    items.forEach((item) => {
      const el = this.renderItem(item);
      this.listContainer.appendChild(el);
    });
  }
  async handleSubmit() {
    let data;
    try {
      data = this.getFormData(); // ممكن يرمي خطأ التحقق
    } catch (validationError) {
      this.showCustomAlert(validationError.message, "error");
      return;
    }

    // الاستمرار في الإرسال إذا كانت البيانات صحيحة
    try {
      const res = await fetch(this.apiBaseUrl, {
        method: "POST",
        headers: {
          "X-CSRFToken": this.csrfToken,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      const result = await res.json();

      if (res.ok) {
        this.showCustomAlert("تمت الإضافة بنجاح", "success");
        this.form.reset();
        this.fetchItems();
      } else {
        this.showCustomAlert(result.message || "فشل الإرسال", "error");
      }
    } catch (error) {
      console.error(error);
      this.showCustomAlert("فشل الاتصال بالخادم.", "error");
    }
  }

//   async handleSubmit() {
//     const data = this.getFormData();
//     try {
//       const res = await fetch(this.apiBaseUrl, {
//         method: "POST",
//         headers: {
//           "X-CSRFToken": this.csrfToken,
//           "Content-Type": "application/json",
//         },
//         body: JSON.stringify(data),
//       });

//       const result = await res.json();

//       if (res.ok) {
//         this.showCustomAlert("تمت الإضافة بنجاح", "success");
//         this.form.reset();
//         this.fetchItems();
//       } else {
//         this.showCustomAlert(result.message || "فشل الإرسال", "error");
//       }
//     } catch (error) {
//       console.error(error);
//       this.showCustomAlert("فشل الاتصال بالخادم.", "error");
//     }
//   }

  async handleDelete(id) {
    if (!confirm("هل أنت متأكد من الحذف؟")) return;

    try {
      const res = await fetch(`${this.apiBaseUrl}${id}/`, {
        method: "DELETE",
        headers: {
          "X-CSRFToken": this.csrfToken,
          "Content-Type": "application/json",
        },
      });

      if (res.ok) {
        this.showCustomAlert("تم الحذف بنجاح", "success");
        this.fetchItems();
      } else {
        const result = await res.json();
        this.showCustomAlert(result.message || "فشل الحذف", "error");
      }
    } catch (error) {
      console.error(error);
      this.showCustomAlert("فشل الاتصال بالحذف.", "error");
    }
  }
  showCustomAlert(message, type = "info") {
    const alertContainer = document.createElement("div");

    // Modernized Design Classes:
    // Increased padding (p-5), stronger shadow (shadow-2xl), better rounded corners (rounded-xl),
    // slightly darker background for better contrast, and subtle border for polish.
    alertContainer.className = `
        fixed bottom-6 right-6 p-5 rounded-xl shadow-2xl text-white z-[999] 
        transition-all duration-300 transform translate-y-full opacity-0
        min-w-[280px] max-w-sm
    `;

    let bgColor = "";
    let iconClass = "";

    // --- Styling based on Alert Type ---
    if (type === "success") {
      // Subtle green background with deeper shadow
      bgColor = "bg-green-600";
      iconClass = "fas fa-check-circle";
    } else if (type === "error") {
      // Strong red background for errors
      bgColor = "bg-red-600";
      iconClass = "fas fa-times-circle";
    } else if (type === "warning") {
      // Added a 'warning' type for amber alerts
      bgColor = "bg-amber-500";
      iconClass = "fas fa-exclamation-triangle";
    } else {
      // Default 'info' type
      bgColor = "bg-blue-600";
      iconClass = "fas fa-info-circle";
    }

    // Apply background color and icon
    alertContainer.classList.add(bgColor);
    alertContainer.innerHTML = `
        <div class="flex items-center">
            <i class="${iconClass} text-2xl mr-4"></i>
            <span class="font-medium">${message}</span>
        </div>
    `;
    document.body.appendChild(alertContainer);

    // --- Animation Logic ---

    // 1. Animate In (Slight delay for smoothness)
    setTimeout(() => {
      alertContainer.classList.remove("translate-y-full", "opacity-0");
      alertContainer.classList.add("translate-y-0", "opacity-100");
    }, 100);

    // 2. Animate Out and Remove (Alert disappears after 5 seconds)
    setTimeout(() => {
      alertContainer.classList.remove("translate-y-0", "opacity-100");
      alertContainer.classList.add("translate-y-full", "opacity-0");
      // Wait for the transition to finish before removing the element
      alertContainer.addEventListener(
        "transitionend",
        () => alertContainer.remove(),
        { once: true }
      );
    }, 5000);
  }
}
