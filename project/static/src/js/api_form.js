class APIFormManager {
  constructor({
    formId,
    listContainerId = null,
    apiBaseUrl,
    endPoint,
    endPoints = [],
    renderItem = null,
    getFormData,
    populateForm = null,
  }) {
    // ... (خصائص الكلاس الأساسية كما هي) ...
    this.form = document.getElementById(formId);
    this.listContainer = listContainerId
      ? document.getElementById(listContainerId)
      : null;
    this.apiBaseUrl = "http://127.0.0.1:8001/api/";
    this.endPoint = endPoint;
    this.endPoints = endPoints;
    this.renderItem = renderItem;
    this.getFormData = getFormData;
    this.populateForm = populateForm;
    this.csrfToken = document.querySelector(
      'input[name="csrfmiddlewaretoken"]'
    )?.value;
    this.editingItemId = null;

    // --- الإضافة الجديدة: التعرف على عناصر المودال ---
    this.deleteModal = document.getElementById("deleteGenericModal");
    if (!this.deleteModal) {
      console.error("Delete modal with ID 'deleteGenericModal' not found.");
      return; // أوقف التنفيذ إذا لم يتم العثور على المودال
    }
    this.modalContent = this.deleteModal.querySelector(".transform");
    this.confirmDeleteBtn = this.deleteModal.querySelector("#confirmDeleteBtn");
    this.modalItemName = this.deleteModal.querySelector("#modalItemName");
    this.modalItemType = this.deleteModal.querySelector("#modalItemType");
    this.closeModalBtns = this.deleteModal.querySelectorAll(".close-modal-btn");

    this.init();
  }

  init() {
    if (this.listContainer && this.renderItem) {
      this.fetchItems();
    }
    if (this.form) {
      this.form.addEventListener("submit", (e) => {
        e.preventDefault();
        this.handleSubmit();
      });
    }
    if (this.listContainer) {
      this.listContainer.addEventListener("click", (e) => {
        const deleteBtn = e.target.closest(".delete-btn");
        if (deleteBtn) {
          // جلب كل البيانات المطلوبة من الزر
          const id = deleteBtn.dataset.id;
          const name = deleteBtn.dataset.name;
          const type = deleteBtn.dataset.type;
          const url = deleteBtn.dataset.url; // مهم جدًا
          if (!id || !name || !type || !url) {
            console.error(
              "Delete button is missing required data attributes (id, name, type, url)."
            );
            this.showCustomAlert("خطأ: بيانات زر الحذف غير مكتملة.", "error");
            return;
          }
          this.handleDelete(id, name, type, url);
          return;
        }

        const editBtn = e.target.closest(".edit-btn");
        if (editBtn) {
          const id = editBtn.dataset.id;
          this.handleEditStart(id);
          return;
        }
      });
    }
  }

  _toggleModalVisibility(show) {
    if (show) {
      this.deleteModal.classList.remove("opacity-0", "invisible");
      this.deleteModal.classList.add("opacity-100", "visible");
      this.modalContent.classList.remove("scale-95", "opacity-0");
      this.modalContent.classList.add("scale-100", "opacity-100");
    } else {
      this.modalContent.classList.add("scale-95", "opacity-0");
      this.modalContent.addEventListener(
        "transitionend",
        () => {
          this.deleteModal.classList.add("opacity-0", "invisible");
        },
        { once: true }
      );
    }
  }

  showDeleteConfirmation(name, type) {
    return new Promise((resolve, reject) => {
      // ملء بيانات المودال
      this.modalItemName.textContent = name;
      this.modalItemType.textContent = type;

      // تعريف دوال التحكم لتسهيل إزالتها لاحقاً
      const onConfirm = () => {
        cleanup();
        resolve();
      };

      const onCancel = () => {
        cleanup();
        reject("cancelled");
      };

      // إضافة مستمعي الأحداث
      this.confirmDeleteBtn.addEventListener("click", onConfirm);
      this.closeModalBtns.forEach((btn) =>
        btn.addEventListener("click", onCancel)
      );
      this.deleteModal.addEventListener("click", (e) => {
        if (e.target === this.deleteModal) {
          onCancel();
        }
      });

      // دالة لتنظيف المستمعين بعد الاستخدام
      const cleanup = () => {
        this.confirmDeleteBtn.removeEventListener("click", onConfirm);
        this.closeModalBtns.forEach((btn) =>
          btn.removeEventListener("click", onCancel)
        );
      };

      // إظهار المودال
      this._toggleModalVisibility(true);
    });
  }

  // --- تم تعديل handleDelete لاستخدام المودال ---
  async handleDelete(id, name, type, url) {
    try {
      await this.showDeleteConfirmation(name, type);

      // 2. إذا وافق المستخدم، استمر في عملية الحذف
      this._toggleModalVisibility(false); // إخفاء المودال

      const res = await fetch(this.apiBaseUrl +url, {
        method: "DELETE",
        headers: {
          "X-CSRFToken": this.csrfToken,
          "Content-Type": "application/json",
        },
      });

      if (res.ok) {
        this.showCustomAlert("تم الحذف بنجاح.", "success");
        if (this.listContainer && this.renderItem) {
          this.fetchItems();
        }
      } else {
        const result = await res.json();
        this.showCustomAlert(result.message || "فشل الحذف.", "error");
      }
    } catch (error) {
      if (error === "cancelled") {
        // المستخدم ألغى العملية
        this._toggleModalVisibility(false);
        console.log("Delete operation was cancelled by the user.");
      } else {
        // حدث خطأ حقيقي
        console.error("HandleDelete Error:", error);
        this.showCustomAlert("حدث خطأ أثناء محاولة الحذف.", "error");
      }
    }
  }

  // ... (بقية دوال الكلاس مثل fetchItems, handleSubmit, showCustomAlert, etc. تبقى كما هي) ...

  // -- يمكنك الاحتفاظ بالدوال الأخرى كما هي --

  async handleEditStart(id) {
    try {
      // عمليات التعديل والحذف عادةً ما تستهدف رابطًا محددًا
      console.log(id);
      const res = await fetch(`${this.apiBaseUrl}${this.endPoint}${id}`);
      if (!res.ok) throw new Error("Failed to fetch item for editing.");
      const item = await res.json();
      if (!this.populateForm) {
        console.error("populateForm function is not provided.");
        this.showCustomAlert("وظيفة تعبئة النموذج غير معرفة.", "error");
        return;
      }
      this.populateForm(item);
      this.editingItemId = id;
      this.updateFormUI(true);
      this.form.scrollIntoView({ behavior: "smooth" });
    } catch (error) {
      console.error(error);
      this.showCustomAlert("فشل في جلب بيانات العنصر للتعديل.", "error");
    }
  }

  cancelEdit() {
    this.editingItemId = null;
    this.form.reset();
    this.updateFormUI(false);
  }

  updateFormUI(isEditing) {
    const submitButton = this.form.querySelector('button[type="submit"]');
    if (!submitButton) return;
    // يمكنك إضافة منطق لتغيير نص الزر هنا، مثلاً
    // submitButton.textContent = isEditing ? 'تحديث' : 'إضافة';
  }

  /**
   * تم تعديل هذه الدالة لجلب البيانات من عدة روابط بالتوازي.
   */

  async fetchItems() {
    // const urlsToFetch =
    //   this.apiBaseUrl + this.endPoints &&this.apiBaseUrl + this.endPoints.length > 0
    //     ?this.apiBaseUrl + this.endPoints
    //     : [this.apiBaseUrl + this.endPoint];
    const urlsToFetch =
    this.endPoints.length > 0
    ? this.endPoints.map((ep) => this.apiBaseUrl + ep)
    : [this.apiBaseUrl + this.endPoint];

    if (urlsToFetch.every((url) => !url)) {
      console.error("No API URLs provided to fetch from.");
      this.showCustomAlert("لم يتم تحديد روابط لجلب البيانات.", "error");
      return;
    }

    try {
      const fetchPromises = urlsToFetch.map((url) =>
        fetch(url).then((res) => {
          if (!res.ok) {
            console.error(`Failed to fetch from ${url}. Status: ${res.status}`);
            return null;
          }
          return res.json();
        })
      );

      const results = await Promise.all(fetchPromises);

      // --- التغيير الأساسي هنا ---
      // لم نعد نستخدم .flat(). ستبقى البيانات في مجموعات منفصلة.
      // dataGroups الآن هي مصفوفة من المصفوفات، مثال: [[programs], [levels]]
      const dataGroups = results.filter(Boolean);

      this.renderList(dataGroups);
    } catch (error) {
      console.error("Error fetching items from multiple sources:", error);
      this.showCustomAlert("فشل تحميل البيانات من المصادر.", "error");
    }
  }

  renderList(dataGroups) {
    // الآن تستقبل مصفوفة من المصفوفات
    if (!this.listContainer || !this.renderItem) return;
    this.listContainer.innerHTML = "";

    // نفترض أن المصفوفة الأولى هي القائمة الأساسية التي نريد عرضها (مثلاً: البرامج)
    const primaryItems = dataGroups[0] || [];

    // بقية المصفوفات هي بيانات إضافية (مثلاً: المستويات)
    const supplementaryData = dataGroups.slice(1);

    if (primaryItems.length === 0) {
      this.listContainer.innerHTML =
        '<p class="text-center text-gray-500 dark:text-gray-300 py-4">لا توجد بيانات لعرضها حاليًا.</p>';
      return;
    }

    // --- التغيير الأساسي هنا ---
    // نمر على كل عنصر في القائمة الأساسية
    primaryItems.forEach((item) => {
      // نستدعي renderItem مع العنصر الأساسي، ونمرر بقية مجموعات البيانات
      // كـ parameters إضافية باستخدام "spread operator (...)"
      const el = this.renderItem(item, ...supplementaryData);
      if (el) {
        this.listContainer.appendChild(el);
      }
    });
  }
  async handleSubmit() {
    let data;
    try {
      data = this.getFormData();
      console.log(data);
    } catch (validationError) {
      this.showCustomAlert(validationError.message, "error");
      return;
    }
    const isEditing = this.editingItemId !== null;
    const url = isEditing
      ? `${this.apiBaseUrl}${this.endPoint}${this.editingItemId}/`
      :this.apiBaseUrl + this.endPoint;
    const method = isEditing ? "PUT" : "POST";
    try {
      const res = await fetch(url, {
        method,
        headers: {
          "X-CSRFToken": this.csrfToken,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });
      if (res.ok) {
        const successMessage = isEditing
          ? "تم التحديث بنجاح"
          : "تمت الإضافة بنجاح";
        this.showCustomAlert(successMessage, "success");
        this.form.reset();
        if (isEditing) this.cancelEdit();
        this.fetchItems();
      } else {
        const result = await res.json();
        const errorMessage = Object.values(result).join("\n");
        this.showCustomAlert(errorMessage || "فشل الإرسال", "error");
      }
    } catch (error) {
      console.error("Submit Error:", error);
      this.showCustomAlert("فشل الاتصال بالخادم.", "error");
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
