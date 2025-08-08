class SearchComponent {
  constructor(params) {
    this.input = document.querySelector(params.inputSelector);
    this.rowsContainer = document.querySelector(params.rowSelector);
    this.noResultsMessage = document.querySelector(params.noResultSelector);
    this.apiEndpoint = params.apiEndpoint;
    this.renderItemFn = params.renderItemFn;

    this.defaultRowsHTML = null; // ❌ لا نحفظ الآن

    if (!this.input || !this.rowsContainer) return;

    // الاستماع لحقل الإدخال
    this.input.addEventListener("input", () => this.handleInput());
  }

  // ✅ تُستدعى هذه بعد ملء المحتوى الأصلي (يدويًا أو من API)
  captureDefaultRows() {
    if (this.rowsContainer && this.defaultRowsHTML === null) {
      this.defaultRowsHTML = this.rowsContainer.innerHTML;
    }
  }

  async handleInput() {
    const query = this.input.value.trim();

    if (!query) {
      if (this.defaultRowsHTML !== null) {
        this.resetToDefault();
      }
      return;
    }

    try {
      const res = await fetch(
        `${this.apiEndpoint}?q=${encodeURIComponent(query)}`
      );
      const data = await res.json();
      this.updateResults(data.results || []);
    } catch (error) {
      console.error("فشل البحث:", error);
    }
  }

  resetToDefault() {
    this.rowsContainer.innerHTML = this.defaultRowsHTML;
    if (this.noResultsMessage) this.noResultsMessage.classList.add("hidden");
  }

  updateResults(results) {
    this.rowsContainer.innerHTML = "";

    if (results.length === 0) {
      if (this.noResultsMessage)
        this.noResultsMessage.classList.remove("hidden");
      return;
    }

    if (this.noResultsMessage) this.noResultsMessage.classList.add("hidden");

    results.forEach((item, index) => {
      const row = this.renderItemFn(item, index);
      this.rowsContainer.insertAdjacentHTML("beforeend", row);
    });
  }
}
