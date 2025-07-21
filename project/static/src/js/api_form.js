class APIFormManager {
  constructor({
    formId,
    listContainerId = null,
    apiBaseUrl,
    renderItem = null,
    getFormData,
  }) {
    this.form = document.getElementById(formId);
    this.listContainer = listContainerId
      ? document.getElementById(listContainerId)
      : null;
    this.apiBaseUrl = apiBaseUrl;
    this.renderItem = renderItem;
    this.getFormData = getFormData;
    this.csrfToken = document.querySelector(
      'input[name="csrfmiddlewaretoken"]'
    )?.value;

    this.init();
  }

  init() {
    // تحميل العناصر فقط إذا تم تمرير listContainer و renderItem
    if (this.listContainer && this.renderItem) {
      this.fetchItems();
    }

    if (this.form) {
      this.form.addEventListener("submit", (e) => {
        e.preventDefault();
        this.handleSubmit();
      });
    }

    // التعامل مع حذف العناصر فقط إذا يوجد listContainer
    if (this.listContainer) {
      this.listContainer.addEventListener("click", (e) => {
        if (e.target.closest(".delete-btn")) {
          const id = e.target.closest(".delete-btn").dataset.id;
          this.handleDelete(id);
        }
      });
    }
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
    if (!this.listContainer || !this.renderItem) return;

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
      data = this.getFormData();
    } catch (validationError) {
      this.showCustomAlert(validationError.message, "error");
      return;
    }

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
        if (this.listContainer && this.renderItem) {
          this.fetchItems();
        }
      } else {
        this.showCustomAlert(result.message || "فشل الإرسال", "error");
      }
    } catch (error) {
      console.error(error);
      this.showCustomAlert("فشل الاتصال بالخادم.", "error");
    }
  }

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
        if (this.listContainer && this.renderItem) {
          this.fetchItems();
        }
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

    alertContainer.className = `
      fixed bottom-6 right-6 p-5 rounded-xl shadow-2xl text-white z-[999]
      transition-all duration-300 transform translate-y-full opacity-0
      min-w-[280px] max-w-sm
    `;

    let bgColor = "";
    let iconClass = "";

    if (type === "success") {
      bgColor = "bg-green-600";
      iconClass = "fas fa-check-circle";
    } else if (type === "error") {
      bgColor = "bg-red-600";
      iconClass = "fas fa-times-circle";
    } else if (type === "warning") {
      bgColor = "bg-amber-500";
      iconClass = "fas fa-exclamation-triangle";
    } else {
      bgColor = "bg-blue-600";
      iconClass = "fas fa-info-circle";
    }

    alertContainer.classList.add(bgColor);
    alertContainer.innerHTML = `
      <div class="flex items-center">
        <i class="${iconClass} text-2xl mr-4"></i>
        <span class="font-medium">${message}</span>
      </div>
    `;

    document.body.appendChild(alertContainer);

    setTimeout(() => {
      alertContainer.classList.remove("translate-y-full", "opacity-0");
      alertContainer.classList.add("translate-y-0", "opacity-100");
    }, 100);

    setTimeout(() => {
      alertContainer.classList.remove("translate-y-0", "opacity-100");
      alertContainer.classList.add("translate-y-full", "opacity-0");
      alertContainer.addEventListener(
        "transitionend",
        () => alertContainer.remove(),
        { once: true }
      );
    }, 5000);
  }
}
