// document.querySelectorAll(".search-input").forEach((input) => {
//   const type = input.getAttribute("data-type");

//   input.addEventListener("keyup", () => {
//     const searchTerm = input.value.toLowerCase().trim();
//     let resultsFound = false;

//     const rows = document.querySelectorAll(`.search-row[data-type="${type}"]`);
//     const noResults = document.querySelector(
//       `.no-results-message[data-type="${type}"]`
//     );

//     rows.forEach((row) => {
//       const name = row.querySelector(".search-name").textContent.toLowerCase();
//       if (name.includes(searchTerm)) {
//         row.style.display = "";
//         resultsFound = true;
//       } else {
//         row.style.display = "none";
//       }
//     });

//     if (noResults) {
//       if (resultsFound) {
//         noResults.classList.add("hidden");
//       } else {
//         noResults.classList.remove("hidden");
//       }
//     }
//   });
// });

class SearchComponent {
  constructor(params) {
    this.input = document.querySelector(params.inputSelector);
    this.rowsContainer = document.querySelector(params.rowSelector);
    this.noResultsMessage = document.querySelector(params.noResultSelector);
    this.apiEndpoint = params.apiEndpoint;
    this.renderItemFn = params.renderItemFn;

    // ✅ حفظ الصفوف الأصلية لإعادة عرضها لاحقًا
    this.defaultRowsHTML = this.rowsContainer
      ? this.rowsContainer.innerHTML
      : "";

    if (!this.input || !this.rowsContainer) return;

    this.input.addEventListener("input", () => this.handleInput());
  }

  async handleInput() {
    const query = this.input.value.trim();
    if (!query) {
      this.resetToDefault();
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
      this.resetToDefault();
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
