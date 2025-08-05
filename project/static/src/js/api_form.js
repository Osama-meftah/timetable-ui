/**
 * APIFormManager Class
 *
 * A comprehensive JavaScript class to manage CRUD operations (Create, Read, Update, Delete)
 * by interacting with a RESTful API, with full support for pagination and multiple data sources.
 *
 * @version 1.0.0
 * @author Your Name
 */
class APIFormManager {
  /**
   * Initializes the manager.
   * @param {object} config - The configuration object.
   * @param {string|null} config.formId - The ID of the form for creating/editing items.
   * @param {string|null} config.listContainerId - The ID of the container (e.g., <tbody>) to render the list of items.
   * @param {string|null} config.paginationContainerId - The ID of the container to render pagination controls.
   * @param {string} config.apiBaseUrl - The base URL for the API (e.g., 'http://127.0.0.1:8001/api/').
   * @param {string} config.endPoint - The primary API endpoint for the main data list (e.g., 'teachers/').
   * @param {string[]} [config.endPoints=[]] - An array of secondary endpoints for supplementary data (e.g., ['programs/', 'levels/']).
   * @param {function|null} config.renderItem - A function that takes an item and supplementary data and returns an HTML element (e.g., a <tr>).
   * @param {function|null} config.getFormData - A function that reads data from the form and returns it as an object.
   * @param {function|null} config.populateForm - A function that takes an item object and populates the form for editing.
   */
  constructor({
    formId,
    listContainerId = null,
    paginationContainerId = null,
    apiBaseUrl,
    editEndPoint,
    endPoint = null,
    endPoints = [],
    renderItem = null,
    getFormData,
    populateForm = null,
  }) {
    // Core Elements
    this.form = formId ? document.getElementById(formId) : null;
    this.listContainer = listContainerId
      ? document.getElementById(listContainerId)
      : null;
    this.renderItem = renderItem;

    this.paginationContainer = paginationContainerId
      ? document.getElementById(paginationContainerId)
      : null;

    // API Configuration
    this.apiBaseUrl = "http://127.0.0.1:8001/api/";
    this.endPoint = endPoint;
    this.endPoints = endPoints;
    editEndPoint = this.endPoint.replace("?paginate=false", "");
    // Callbacks
    // this.renderItem = renderItem;
    this.getFormData = getFormData;
    this.populateForm = populateForm;

    // State Management
    this.editingItemId = null;
    this.currentPageUrl = null; // Stores the URL of the currently displayed page
    this.csrfToken = document.querySelector(
      'input[name="csrfmiddlewaretoken"]'
    )?.value;

    // Modal Elements
    this.deleteModal = document.getElementById("deleteGenericModal");
    if (this.deleteModal) {
      this.modalContent = this.deleteModal.querySelector(".transform");
      this.confirmDeleteBtn =
        this.deleteModal.querySelector("#confirmDeleteBtn");
      this.modalItemName = this.deleteModal.querySelector("#modalItemName");
      this.modalItemType = this.deleteModal.querySelector("#modalItemType");
      this.closeModalBtns =
        this.deleteModal.querySelectorAll(".close-modal-btn");
    }

    this.init();
  }

  /**
   * Initializes event listeners for the form, list, and pagination.
   */
  init() {
    // Fetch initial data on load
    if (this.listContainer && this.renderItem) {
      this.fetchItems();
    }

    // Form submission listener
    if (this.form) {
      this.form.addEventListener("submit", (e) => {
        e.preventDefault();
        this.handleSubmit();
      });
    }

    // List container listener for edit/delete actions
    if (this.listContainer) {
      this.listContainer.addEventListener("click", (e) => {
        const deleteBtn = e.target.closest(".delete-btn");
        if (deleteBtn) {
          const { id, name, type, url } = deleteBtn.dataset;
          if (!id || !name || !type || !url) {
            this.showCustomAlert("خطأ: بيانات زر الحذف غير مكتملة.", "error");
            return;
          }
          this.handleDelete(id, name, type, url);
          return;
        }
        const editBtn = e.target.closest(".edit-btn");
        if (editBtn) {
          this.handleEditStart(editBtn.dataset.id);
        }
      });
    }

    // Pagination container listener
    if (this.paginationContainer) {
      this.paginationContainer.addEventListener("click", (e) => {
        const pageLink = e.target.closest("button[data-url]");
        if (pageLink && !pageLink.disabled) {
          this.fetchItems(pageLink.dataset.url);
        }
      });
    }
  }

  async fetchItems(primaryUrl = null) {
    // ==========================================================
    // الخطوة 1: بناء الرابط الأساسي بأمان
    // ==========================================================
    let mainUrlToFetch = primaryUrl;

    if (!mainUrlToFetch) {
      // إذا لم يتم تمرير رابط، قم ببنائه من الـ endPoint
      if (this.endPoint) {
        mainUrlToFetch = this.apiBaseUrl + this.endPoint;
      } else {
        // لا يوجد رابط أساسي، وهذا قد يكون طبيعيًا إذا كانت
        // البيانات الأساسية تأتي من أول رابط في endPoints
        console.warn(
          "Primary 'endPoint' is not defined for this manager. Relying on 'endPoints' array."
        );
      }
    }

    // ==========================================================
    // الخطوة 2: بناء قائمة الروابط الكاملة وتصفيتها
    // ==========================================================
    const secondaryUrls = this.endPoints.map((ep) => this.apiBaseUrl + ep);

    // استخدم Set لإزالة الروابط المكررة (إذا كان endPoint موجودًا أيضًا في endPoints)
    const uniqueUrls = new Set([mainUrlToFetch, ...secondaryUrls]);

    // قم بتصفية أي قيم فارغة أو null أو undefined
    const urlsToFetch = Array.from(uniqueUrls).filter((url) => url);

    if (urlsToFetch.length === 0) {
      console.error(
        "No valid API URLs to fetch. Check 'endPoint' and 'endPoints' configuration."
      );
      this.showCustomAlert("خطأ: لم يتم تحديد روابط لجلب البيانات.", "error");
      return;
    }

    // تخزين الرابط الحالي للتنقل
    this.currentPageUrl = mainUrlToFetch || urlsToFetch[0];

    // ==========================================================
    // الخطوة 3: جلب البيانات ومعالجتها (الكود الخاص بك مع تحسينات بسيطة)
    // ==========================================================
    try {
      const fetchPromises = urlsToFetch.map((url) =>
        fetch(url).then((res) => {
          if (!res.ok) {
            // نوفر رسالة خطأ أوضح
            console.error(
              `Failed to fetch from ${url}. Status: ${res.status} ${res.statusText}`
            );
            return null;
          }
          return res.json();
        })
      );

      const results = await Promise.all(fetchPromises);
      const [primaryResponse, ...supplementaryData] = results.filter(Boolean);

      let primaryItems = [];
      let startIndex = 0;

      // تحقق إذا كانت الاستجابة مقسمة إلى صفحات
      if (
        primaryResponse &&
        typeof primaryResponse === "object" &&
        "results" in primaryResponse
      ) {
        primaryItems = primaryResponse.results;
        const currentPage =
          primaryResponse.current_page ||
          parseInt(
            new URLSearchParams(this.currentPageUrl.split("?")[1]).get(
              "page"
            ) || "1"
          );
        const pageSize = primaryItems.length || 10;
        startIndex = (currentPage - 1) * pageSize;
        this.renderPagination(primaryResponse);
      } else {
        primaryItems = primaryResponse || [];
        if (this.paginationContainer) this.paginationContainer.innerHTML = "";
      }

      this.renderList([primaryItems, ...supplementaryData], startIndex);
    } catch (error) {
      console.error("Error fetching items from multiple sources:", error);
      this.showCustomAlert(`فشل تحميل البيانات: ${error.message}`, "error");
    }
  }
  renderList(dataGroups) {
    if (!this.listContainer || !this.renderItem) return;
    this.listContainer.innerHTML = "";

    const [primaryItems, ...supplementaryData] = dataGroups;

    if (primaryItems.length === 0) {
      this.listContainer.innerHTML =
        '<tr><td colspan="100%" class="text-center text-gray-500 py-8">لا توجد بيانات لعرضها حاليًا.</td></tr>';
      return;
    }

    primaryItems.forEach((item, index) => {
      const el = this.renderItem(item, ...supplementaryData, index);
      if (el) {
        this.listContainer.appendChild(el);
      }
    });
  }

  renderPagination(paginationData) {
    if (!this.paginationContainer) return;

    const { count, total_pages, links } = paginationData;
    this.paginationContainer.innerHTML = "";
    if (!count || total_pages <= 1) return;

    // Calculate current page number
    let currentPage = 1;
    const urlParams = new URLSearchParams(this.currentPageUrl.split("?")[1]);
    if (urlParams.has("page")) {
      currentPage = parseInt(urlParams.get("page"));
    }

    let pageButtonsHTML = "";
    let lastPageRendered = 0;

    // Build page number buttons
    for (let i = 1; i <= total_pages; i++) {
      const isCurrent = i === currentPage;
      const inRange = i >= currentPage - 2 && i <= currentPage + 2;

      if (i === 1 || i === total_pages || inRange) {
        if (i > lastPageRendered + 1) {
          pageButtonsHTML += `<span class="px-2 select-none">...</span>`;
        }

        const activeClass = isCurrent
          ? "bg-indigo-600 text-white"
          : "text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 border border-gray-300 dark:border-gray-600";

        const url = new URL(this.currentPageUrl, this.apiBaseUrl); // Use base URL for relative URLs
        url.searchParams.set("page", i);

        pageButtonsHTML += `
          <button data-url="${url.href}" class="relative inline-flex items-center px-4 py-2 text-sm font-medium rounded-md ${activeClass} transition-colors duration-200">
            ${i}
          </button>
        `;
        lastPageRendered = i;
      }
    }

    // Build 'Previous' and 'Next' buttons
    const prevButton = links.previous
      ? `<button data-url="${links.previous}" class="relative inline-flex items-center px-4 py-2 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 border border-gray-300 dark:border-gray-600 transition-colors duration-200">السابق</button>`
      : `<span class="relative inline-flex items-center px-4 py-2 text-sm font-medium rounded-md text-gray-400 dark:text-gray-500 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 cursor-not-allowed">السابق</span>`;

    const nextButton = links.next
      ? `<button data-url="${links.next}" class="relative inline-flex items-center px-4 py-2 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 border border-gray-300 dark:border-gray-600 transition-colors duration-200">التالي</button>`
      : `<span class="relative inline-flex items-center px-4 py-2 text-sm font-medium rounded-md text-gray-400 dark:text-gray-500 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 cursor-not-allowed">التالي</span>`;

    this.paginationContainer.innerHTML = `
      <nav class="flex items-center justify-center pt-6">
        <div class="flex items-center gap-2">
          ${prevButton}
          ${pageButtonsHTML}
          ${nextButton}
        </div>
      </nav>
    `;
  }

  /**
   * Handles form submission for both creating and updating items.
   */
  async handleSubmit() {
    let data;
    try {
      data = this.getFormData();
    } catch (validationError) {
      this.showCustomAlert(validationError.message, "error");
      return;
    }
    console.log(data);
    const isEditing = this.editingItemId !== null;
    const url = isEditing
      ? `${this.apiBaseUrl}${this.editEndPoint}${this.editingItemId}/`
      : `${this.apiBaseUrl}${this.endPoint}`;
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
        this.showCustomAlert(
          isEditing ? "تم التحديث بنجاح" : "تمت الإضافة بنجاح",
          "success"
        );
        document.dispatchEvent(new CustomEvent("dataChanged"));
        if (this.form) this.form.reset();
        if (isEditing) this.cancelEdit();
        // After editing, reload the current page. After creating, go to the first page.
        this.fetchItems(isEditing ? this.currentPageUrl : null);
      } else {
        const result = await res.json();
        const errorMessage = Object.values(
          result.errors || { error: result.message }
        )
          .flat()
          .join("\n");
        this.showCustomAlert(errorMessage || "فشل الإرسال.", "error");
      }
    } catch (error) {
      console.error("Submit Error:", error);
      this.showCustomAlert("فشل الاتصال بالخادم.", "error");
    }
  }

  async handleDelete(id, name, type, url) {
    try {
      await this.showDeleteConfirmation(name, type);
      this._toggleModalVisibility(false);

      const res = await fetch(`${this.apiBaseUrl}${url}`, {
        method: "DELETE",
        headers: { "X-CSRFToken": this.csrfToken },
      });

      if (res.ok) {
        this.showCustomAlert("تم الحذف بنجاح.", "success");
        document.dispatchEvent(new CustomEvent("dataChanged"));
        // Reload the current page to reflect the deletion
        this.fetchItems(this.currentPageUrl);
      } else {
        const result = await res.json();
        this.showCustomAlert(result.message || "فشل الحذف.", "error");
      }
    } catch (error) {
      if (error === "cancelled") {
        this._toggleModalVisibility(false);
      } else {
        console.error("HandleDelete Error:", error);
        this.showCustomAlert("حدث خطأ أثناء محاولة الحذف.", "error");
      }
    }
  }
  async handleEditStart(id) {
    try {
      console.log(id);
       this.editEndPoint = this.endPoint.replace("?paginate=false", "");
      console.log(this.editEndPoint);

      const res = await fetch(`${this.apiBaseUrl}${this.editEndPoint}${id}/`);
      if (!res.ok) throw new Error("Failed to fetch item for editing.");
      const item = await res.json();

      if (this.populateForm) {
        this.populateForm(item);
        this.editingItemId = id;
        this.updateFormUI(true);
        if (this.form)
          this.form.scrollIntoView({ behavior: "smooth", block: "start" });
      } else {
        this.showCustomAlert("وظيفة تعبئة النموذج غير معرفة.", "error");
      }
    } catch (error) {
      console.error(error);
      this.showCustomAlert("فشل في جلب بيانات العنصر للتعديل.", "error");
    }
  }

  /**
   * Resets the form and editing state.
   */
  cancelEdit() {
    this.editingItemId = null;
    if (this.form) this.form.reset();
    this.updateFormUI(false);
  }

  /**
   * Updates the form's UI to reflect editing state (e.g., button text).
   * @param {boolean} isEditing - True if the form is in editing mode.
   */
  updateFormUI(isEditing) {
    if (!this.form) return;
    const submitButton = this.form.querySelector('button[type="submit"]');
    if (submitButton) {
      // Example: Change button text
      // submitButton.textContent = isEditing ? 'تحديث' : 'إضافة';
    }
    const cancelButton = this.form.querySelector(".cancel-edit-btn");
    if (cancelButton) {
      cancelButton.style.display = isEditing ? "inline-block" : "none";
    }
  }

  // --- MODAL AND ALERT UTILITY FUNCTIONS ---

  showDeleteConfirmation(name, type) {
    return new Promise((resolve, reject) => {
      if (!this.deleteModal) return reject("Modal not found");
      this.modalItemName.textContent = name;
      this.modalItemType.textContent = type;

      const onConfirm = () => {
        cleanup();
        resolve();
      };
      const onCancel = () => {
        cleanup();
        reject("cancelled");
      };

      const cleanup = () => {
        this.confirmDeleteBtn.removeEventListener("click", onConfirm);
        this.closeModalBtns.forEach((btn) =>
          btn.removeEventListener("click", onCancel)
        );
      };

      this.confirmDeleteBtn.addEventListener("click", onConfirm, {
        once: true,
      });
      this.closeModalBtns.forEach((btn) =>
        btn.addEventListener("click", onCancel, { once: true })
      );

      this._toggleModalVisibility(true);
    });
  }

  _toggleModalVisibility(show) {
    if (!this.deleteModal) return;
    if (show) {
      this.deleteModal.classList.remove("opacity-0", "invisible");
      this.modalContent?.classList.remove("scale-95", "opacity-0");
    } else {
      this.modalContent?.classList.add("scale-95", "opacity-0");
      this.modalContent?.addEventListener(
        "transitionend",
        () => {
          this.deleteModal.classList.add("opacity-0", "invisible");
        },
        { once: true }
      );
    }
  }

  showCustomAlert(message, type = "info") {
    const alertContainer = document.createElement("div");
    const styles = {
      success: { bg: "bg-green-600", icon: "fa-check-circle" },
      error: { bg: "bg-red-600", icon: "fa-times-circle" },
      warning: { bg: "bg-amber-500", icon: "fa-exclamation-triangle" },
      info: { bg: "bg-blue-600", icon: "fa-info-circle" },
    };
    const style = styles[type] || styles.info;

    alertContainer.className = `fixed bottom-6 right-6 p-5 rounded-xl shadow-2xl text-white z-[999] transition-all duration-300 transform translate-y-full opacity-0 min-w-[280px] max-w-sm ${style.bg}`;
    alertContainer.innerHTML = `<div class="flex items-center"><i class="fas ${style.icon} text-2xl mr-4"></i><span class="font-medium">${message}</span></div>`;

    document.body.appendChild(alertContainer);

    setTimeout(() => {
      alertContainer.classList.remove("translate-y-full", "opacity-0");
    }, 100);

    setTimeout(() => {
      alertContainer.classList.add("translate-y-full", "opacity-0");
      alertContainer.addEventListener(
        "transitionend",
        () => alertContainer.remove(),
        { once: true }
      );
    }, 5000);
  }
}

// class APIFormManager {
//   constructor({
//     formId,
//     listContainerId = null,
//     apiBaseUrl,
//     endPoint,
//     endPoints = [],
//     renderItem = null,
//     getFormData,
//     populateForm = null,
//   }) {
//     // ... (خصائص الكلاس الأساسية كما هي) ...
//     this.form = document.getElementById(formId);
//     this.listContainer = listContainerId
//       ? document.getElementById(listContainerId)
//       : null;
//     this.apiBaseUrl = "http://127.0.0.1:8001/api/";
//     this.endPoint = endPoint;
//     this.endPoints = endPoints;
//     this.renderItem = renderItem;
//     this.getFormData = getFormData;
//     this.populateForm = populateForm;
//     this.csrfToken = document.querySelector(
//       'input[name="csrfmiddlewaretoken"]'
//     )?.value;
//     this.editingItemId = null;

//     // --- الإضافة الجديدة: التعرف على عناصر المودال ---
//     this.deleteModal = document.getElementById("deleteGenericModal");
//     if (!this.deleteModal) {
//       console.error("Delete modal with ID 'deleteGenericModal' not found.");
//       return; // أوقف التنفيذ إذا لم يتم العثور على المودال
//     }
//     this.modalContent = this.deleteModal.querySelector(".transform");
//     this.confirmDeleteBtn = this.deleteModal.querySelector("#confirmDeleteBtn");
//     this.modalItemName = this.deleteModal.querySelector("#modalItemName");
//     this.modalItemType = this.deleteModal.querySelector("#modalItemType");
//     this.closeModalBtns = this.deleteModal.querySelectorAll(".close-modal-btn");

//     this.init();
//   }

//   init() {
//     if (this.listContainer && this.renderItem) {
//       this.fetchItems();
//     }
//     if (this.form) {
//       this.form.addEventListener("submit", (e) => {
//         e.preventDefault();
//         this.handleSubmit();
//       });
//     }
//     if (this.listContainer) {
//       this.listContainer.addEventListener("click", (e) => {
//         const deleteBtn = e.target.closest(".delete-btn");
//         if (deleteBtn) {
//           // جلب كل البيانات المطلوبة من الزر
//           const id = deleteBtn.dataset.id;
//           const name = deleteBtn.dataset.name;
//           const type = deleteBtn.dataset.type;
//           const url = deleteBtn.dataset.url; // مهم جدًا
//           if (!id || !name || !type || !url) {
//             console.error(
//               "Delete button is missing required data attributes (id, name, type, url)."
//             );
//             this.showCustomAlert("خطأ: بيانات زر الحذف غير مكتملة.", "error");
//             return;
//           }
//           this.handleDelete(id, name, type, url);
//           return;
//         }

//         const editBtn = e.target.closest(".edit-btn");
//         if (editBtn) {
//           const id = editBtn.dataset.id;
//           this.handleEditStart(id);
//           return;
//         }
//       });
//     }
//   }

//   _toggleModalVisibility(show) {
//     if (show) {
//       this.deleteModal.classList.remove("opacity-0", "invisible");
//       this.deleteModal.classList.add("opacity-100", "visible");
//       this.modalContent.classList.remove("scale-95", "opacity-0");
//       this.modalContent.classList.add("scale-100", "opacity-100");
//     } else {
//       this.modalContent.classList.add("scale-95", "opacity-0");
//       this.modalContent.addEventListener(
//         "transitionend",
//         () => {
//           this.deleteModal.classList.add("opacity-0", "invisible");
//         },
//         { once: true }
//       );
//     }
//   }

//   showDeleteConfirmation(name, type) {
//     return new Promise((resolve, reject) => {
//       // ملء بيانات المودال
//       this.modalItemName.textContent = name;
//       this.modalItemType.textContent = type;

//       // تعريف دوال التحكم لتسهيل إزالتها لاحقاً
//       const onConfirm = () => {
//         cleanup();
//         resolve();
//       };

//       const onCancel = () => {
//         cleanup();
//         reject("cancelled");
//       };

//       // إضافة مستمعي الأحداث
//       this.confirmDeleteBtn.addEventListener("click", onConfirm);
//       this.closeModalBtns.forEach((btn) =>
//         btn.addEventListener("click", onCancel)
//       );
//       this.deleteModal.addEventListener("click", (e) => {
//         if (e.target === this.deleteModal) {
//           onCancel();
//         }
//       });

//       // دالة لتنظيف المستمعين بعد الاستخدام
//       const cleanup = () => {
//         this.confirmDeleteBtn.removeEventListener("click", onConfirm);
//         this.closeModalBtns.forEach((btn) =>
//           btn.removeEventListener("click", onCancel)
//         );
//       };

//       // إظهار المودال
//       this._toggleModalVisibility(true);
//     });
//   }

//   // --- تم تعديل handleDelete لاستخدام المودال ---
//   async handleDelete(id, name, type, url) {
//     try {
//       await this.showDeleteConfirmation(name, type);

//       // 2. إذا وافق المستخدم، استمر في عملية الحذف
//       this._toggleModalVisibility(false); // إخفاء المودال

//       const res = await fetch(this.apiBaseUrl + url, {
//         method: "DELETE",
//         headers: {
//           "X-CSRFToken": this.csrfToken,
//           "Content-Type": "application/json",
//         },
//       });

//       if (res.ok) {
//         this.showCustomAlert("تم الحذف بنجاح.", "success");
//         if (this.listContainer && this.renderItem) {
//           this.fetchItems();
//         }
//       } else {
//         const result = await res.json();
//         this.showCustomAlert(result.message || "فشل الحذف.", "error");
//       }
//     } catch (error) {
//       if (error === "cancelled") {
//         // المستخدم ألغى العملية
//         this._toggleModalVisibility(false);
//         console.log("Delete operation was cancelled by the user.");
//       } else {
//         // حدث خطأ حقيقي
//         console.error("HandleDelete Error:", error);
//         this.showCustomAlert("حدث خطأ أثناء محاولة الحذف.", "error");
//       }
//     }
//   }

//   // ... (بقية دوال الكلاس مثل fetchItems, handleSubmit, showCustomAlert, etc. تبقى كما هي) ...

//   // -- يمكنك الاحتفاظ بالدوال الأخرى كما هي --

//   async handleEditStart(id) {
//     try {
//       // عمليات التعديل والحذف عادةً ما تستهدف رابطًا محددًا
//       console.log(id);
//       const res = await fetch(`${this.apiBaseUrl}${this.endPoint}${id}`);
//       if (!res.ok) throw new Error("Failed to fetch item for editing.");
//       const item = await res.json();
//       if (!this.populateForm) {
//         console.error("populateForm function is not provided.");
//         this.showCustomAlert("وظيفة تعبئة النموذج غير معرفة.", "error");
//         return;
//       }
//       this.populateForm(item);
//       this.editingItemId = id;
//       this.updateFormUI(true);
//       this.form.scrollIntoView({ behavior: "smooth" });
//     } catch (error) {
//       console.error(error);
//       this.showCustomAlert("فشل في جلب بيانات العنصر للتعديل.", "error");
//     }
//   }

//   cancelEdit() {
//     this.editingItemId = null;
//     this.form.reset();
//     this.updateFormUI(false);
//   }

//   updateFormUI(isEditing) {
//     const submitButton = this.form.querySelector('button[type="submit"]');
//     if (!submitButton) return;
//     // يمكنك إضافة منطق لتغيير نص الزر هنا، مثلاً
//     // submitButton.textContent = isEditing ? 'تحديث' : 'إضافة';
//   }

//   /**
//    * تم تعديل هذه الدالة لجلب البيانات من عدة روابط بالتوازي.
//    */

//   async fetchItems() {
//     // const urlsToFetch =
//     //   this.apiBaseUrl + this.endPoints &&this.apiBaseUrl + this.endPoints.length > 0
//     //     ?this.apiBaseUrl + this.endPoints
//     //     : [this.apiBaseUrl + this.endPoint];
//     const urlsToFetch =
//       this.endPoints.length > 0
//         ? this.endPoints.map((ep) => this.apiBaseUrl + ep)
//         : [this.apiBaseUrl + this.endPoint];

//     if (urlsToFetch.every((url) => !url)) {
//       console.error("No API URLs provided to fetch from.");
//       this.showCustomAlert("لم يتم تحديد روابط لجلب البيانات.", "error");
//       return;
//     }

//     try {
//       const fetchPromises = urlsToFetch.map((url) =>
//         fetch(url).then((res) => {
//           if (!res.ok) {
//             console.error(`Failed to fetch from ${url}. Status: ${res.status}`);
//             return null;
//           }
//           return res.json();
//         })
//       );

//       const results = await Promise.all(fetchPromises);

//       // --- التغيير الأساسي هنا ---
//       // لم نعد نستخدم .flat(). ستبقى البيانات في مجموعات منفصلة.
//       // dataGroups الآن هي مصفوفة من المصفوفات، مثال: [[programs], [levels]]
//       const dataGroups = results.filter(Boolean);

//       this.renderList(dataGroups);
//     } catch (error) {
//       console.error("Error fetching items from multiple sources:", error);
//       this.showCustomAlert("فشل تحميل البيانات من المصادر.", "error");
//     }
//   }

//   renderList(dataGroups) {
//     // الآن تستقبل مصفوفة من المصفوفات
//     if (!this.listContainer || !this.renderItem) return;
//     this.listContainer.innerHTML = "";

//     // نفترض أن المصفوفة الأولى هي القائمة الأساسية التي نريد عرضها (مثلاً: البرامج)
//     const primaryItems = dataGroups[0] || [];

//     // بقية المصفوفات هي بيانات إضافية (مثلاً: المستويات)
//     const supplementaryData = dataGroups.slice(1);

//     if (primaryItems.length === 0) {
//       this.listContainer.innerHTML =
//         '<p class="text-center text-gray-500 dark:text-gray-300 py-4">لا توجد بيانات لعرضها حاليًا.</p>';
//       return;
//     }

//     // --- التغيير الأساسي هنا ---
//     // نمر على كل عنصر في القائمة الأساسية
//     primaryItems.forEach((item) => {
//       // نستدعي renderItem مع العنصر الأساسي، ونمرر بقية مجموعات البيانات
//       // كـ parameters إضافية باستخدام "spread operator (...)"
//       const el = this.renderItem(item, ...supplementaryData);
//       if (el) {
//         this.listContainer.appendChild(el);
//       }
//     });
//   }
//   async handleSubmit() {
//     let data;
//     try {
//       data = this.getFormData();
//       console.log(data);
//     } catch (validationError) {
//       this.showCustomAlert(validationError.message, "error");
//       return;
//     }
//     const isEditing = this.editingItemId !== null;
//     const url = isEditing
//       ? `${this.apiBaseUrl}${this.endPoint}${this.editingItemId}/`
//       : this.apiBaseUrl + this.endPoint;
//     const method = isEditing ? "PUT" : "POST";
//     try {
//       const res = await fetch(url, {
//         method,
//         headers: {
//           "X-CSRFToken": this.csrfToken,
//           "Content-Type": "application/json",
//         },
//         body: JSON.stringify(data),
//       });
//       if (res.ok) {
//         const successMessage = isEditing
//           ? "تم التحديث بنجاح"
//           : "تمت الإضافة بنجاح";
//         this.showCustomAlert(successMessage, "success");
//         this.form.reset();
//         if (isEditing) this.cancelEdit();
//         this.fetchItems();
//       } else {
//         const result = await res.json();
//         const errorMessage = Object.values(result).join("\n");
//         this.showCustomAlert(errorMessage || "فشل الإرسال", "error");
//       }
//     } catch (error) {
//       console.error("Submit Error:", error);
//       this.showCustomAlert("فشل الاتصال بالخادم.", "error");
//     }
//   }
//   showCustomAlert(message, type = "info") {
//     const alertContainer = document.createElement("div");
//     alertContainer.className = `
//       fixed bottom-6 right-6 p-5 rounded-xl shadow-2xl text-white z-[999]
//       transition-all duration-300 transform translate-y-full opacity-0
//       min-w-[280px] max-w-sm
//     `;
//     let bgColor = "";
//     let iconClass = "";
//     if (type === "success") {
//       bgColor = "bg-green-600";
//       iconClass = "fas fa-check-circle";
//     } else if (type === "error") {
//       bgColor = "bg-red-600";
//       iconClass = "fas fa-times-circle";
//     } else if (type === "warning") {
//       bgColor = "bg-amber-500";
//       iconClass = "fas fa-exclamation-triangle";
//     } else {
//       bgColor = "bg-blue-600";
//       iconClass = "fas fa-info-circle";
//     }
//     alertContainer.classList.add(bgColor);
//     alertContainer.innerHTML = `
//       <div class="flex items-center">
//         <i class="${iconClass} text-2xl mr-4"></i>
//         <span class="font-medium">${message}</span>
//       </div>
//     `;
//     document.body.appendChild(alertContainer);
//     setTimeout(() => {
//       alertContainer.classList.remove("translate-y-full", "opacity-0");
//       alertContainer.classList.add("translate-y-0", "opacity-100");
//     }, 100);
//     setTimeout(() => {
//       alertContainer.classList.remove("translate-y-0", "opacity-100");
//       alertContainer.classList.add("translate-y-full", "opacity-0");
//       alertContainer.addEventListener(
//         "transitionend",
//         () => alertContainer.remove(),
//         { once: true }
//       );
//     }, 5000);
//   }
// }
