/**
 * APIFormManager Class (مع وظيفة البحث المدمجة)
 *
 * كلاس شامل لإدارة عمليات CRUD، التنقل، العرض، والبحث الديناميكي من API.
 * @version 2.0.0
 */
class APIFormManager {
  constructor({
    formId,
    // listContainerId,
    listContainerId = null,
    paginationContainerId = null,
    apiBaseUrl,
    endPoint,
    endPoints = [],
    renderItem,
    getFormData = null,
    populateForm = null,
    // --- الإضافات الجديدة للبحث ---
    searchInputSelector = null,
    searchEndPoint = null,
  }) {
    // العناصر الأساسية
    this.form = formId ? document.getElementById(formId) : null;
    // this.listContainer = document.getElementById(listContainerId);
    this.listContainer = listContainerId
      ? document.getElementById(listContainerId)
      : null;
    this.paginationContainer = paginationContainerId
      ? document.getElementById(paginationContainerId)
      : null;

    // إعدادات الـ API
    this.apiBaseUrl = apiBaseUrl || "http://127.0.0.1:8001/api/";
    this.endPoint = endPoint;
    this.endPoints = endPoints;

    // دوال رد النداء
    this.renderItem = renderItem;
    this.getFormData = getFormData;
    this.populateForm = populateForm;

    // إعدادات البحث
    this.searchInput = searchInputSelector
      ? document.querySelector(searchInputSelector)
      : null;
    this.searchEndPoint = searchEndPoint;

    // إدارة الحالة
    this.editingItemId = null;
    this.currentPageUrl = null;
    this.csrfToken = document.querySelector(
      'input[name="csrfmiddlewaretoken"]'
    )?.value;
    this.supplementaryDataStore = [];
    this.primaryDataStore = [];
    this.isSearching = false;

    // عناصر المودال
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

    // if (!this.listContainer) {
    //   console.error("Critical error: 'listContainerId' is required.");
    //   return;
    // }
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
if (this.listContainer && this.renderItem) {
            // جلب البيانات الأولية
            this.fetchItems();

            // مستمع لأزرار التعديل/الحذف في القائمة
            this.listContainer.addEventListener("click", (e) => {
                const deleteBtn = e.target.closest(".delete-btn");
                if (deleteBtn) {
                    const { id, name, type, url } = deleteBtn.dataset;
                    this.handleDelete(id, name, type, url);
                    return;
                }
                const editBtn = e.target.closest(".edit-btn");
                if (editBtn) this.handleEditStart(editBtn.dataset.id);
            });
  
    // if (this.listContainer) {
    //   this.listContainer.addEventListener("click", (e) => {
    //     const deleteBtn = e.target.closest(".delete-btn");
    //     if (deleteBtn) {
    //       const { id, name, type, url } = deleteBtn.dataset;
    //       this.handleDelete(id, name, type, url);
    //       return;
    //     }
    //     const editBtn = e.target.closest(".edit-btn");
    //     if (editBtn) this.handleEditStart(editBtn.dataset.id);
    //   });
    }

    if (this.paginationContainer) {
      this.paginationContainer.addEventListener("click", (e) => {
        const pageButton = e.target.closest("button[data-url]");
        if (pageButton) this.fetchItems(pageButton.dataset.url);
      });
    }

    if (this.searchInput && this.searchEndPoint) {
      let debounceTimer;
      this.searchInput.addEventListener("input", () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => this.handleSearch(), 300);
      });
    }
  }

  async handleSearch() {
    const query = this.searchInput.value.trim();

    if (!query) {
      this.isSearching = false;
      this.fetchItems(this.apiBaseUrl + this.endPoint);
      return;
    }

    this.isSearching = true;
    if (this.paginationContainer)
      this.paginationContainer.style.display = "none";

    try {
      const searchUrl = `${this.apiBaseUrl}${
        this.searchEndPoint
      }?q=${encodeURIComponent(query)}`;
      const res = await fetch(searchUrl);
      const data = await res.json();
      this.renderList([data.results || []]);
    } catch (error) {
      console.error("Search failed:", error);
      this.listContainer.innerHTML =
        '<tr><td colspan="100%">فشل البحث.</td></tr>';
    }
  }

  async fetchItems(primaryUrl = null) {
    if (this.paginationContainer)
      this.paginationContainer.style.display = "block";

    let mainUrlToFetch = primaryUrl;
    if (!mainUrlToFetch && this.endPoint) {
      mainUrlToFetch = this.apiBaseUrl + this.endPoint;
    }

    const secondaryUrls = this.endPoints.map((ep) => this.apiBaseUrl + ep);
    const uniqueUrls = new Set([mainUrlToFetch, ...secondaryUrls]);
    const urlsToFetch = Array.from(uniqueUrls).filter((url) => url);

    if (urlsToFetch.length === 0) return;
    this.currentPageUrl = mainUrlToFetch || urlsToFetch[0];

    try {
      const fetchPromises = urlsToFetch.map((url) =>
        fetch(url).then((res) => (res.ok ? res.json() : null))
      );
      const results = await Promise.all(fetchPromises);
      const [primaryResponse, ...supplementaryData] = results.filter(Boolean);

      this.supplementaryDataStore = supplementaryData;

      let primaryItems = [];
      if (
        primaryResponse &&
        typeof primaryResponse === "object" &&
        "results" in primaryResponse
      ) {
        primaryItems = primaryResponse.results;
        this.renderPagination(primaryResponse);
      } else {
        primaryItems = Array.isArray(primaryResponse) ? primaryResponse : [];
        if (this.paginationContainer) this.paginationContainer.innerHTML = "";
      }

      this.primaryDataStore = primaryItems;
      this.renderList([primaryItems, ...supplementaryData]);
    } catch (error) {
      console.error("Error fetching items:", error);
    }
  }

  renderList(dataGroups, startIndex = 0) {
    if (!this.listContainer || !this.renderItem) return;
    this.listContainer.innerHTML = "";
    const [primaryItems, ...supplementaryData] = dataGroups;
    if (primaryItems.length === 0) {
      const message = this.isSearching
        ? "لا توجد نتائج مطابقة لبحثك."
        : "لا توجد بيانات لعرضها.";
      this.listContainer.innerHTML = `<tr><td colspan="100%" class="text-center py-8">${message}</td></tr>`;
      return;
    }
    primaryItems.forEach((item, index) => {
      const itemIndex = startIndex + index;
      const el = this.renderItem(item, ...supplementaryData, itemIndex);
      if (el) this.listContainer.appendChild(el);
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
  fetchData(params = {}) {
    let url = this.apiBaseUrl + this.endPoint;

    // إضافة المعاملات (parameters) إذا كانت موجودة
    const query = new URLSearchParams(params).toString();
    if (query) {
        url += `?${query}`;
    }

    this.fetchItems(url) // استخدم fetchItems مع الرابط الجديد
  }
  // استخدم fetchItems مع الرابط الجديد


}
