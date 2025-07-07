document.querySelectorAll(".search-input").forEach((input) => {
  const type = input.getAttribute("data-type");

  input.addEventListener("keyup", () => {
    const searchTerm = input.value.toLowerCase().trim();
    let resultsFound = false;

    const rows = document.querySelectorAll(`.search-row[data-type="${type}"]`);
    const noResults = document.querySelector(
      `.no-results-message[data-type="${type}"]`
    );

    rows.forEach((row) => {
      const name = row.querySelector(".search-name").textContent.toLowerCase();
      if (name.includes(searchTerm)) {
        row.style.display = "";
        resultsFound = true;
      } else {
        row.style.display = "none";
      }
    });

    if (noResults) {
      if (resultsFound) {
        noResults.classList.add("hidden");
      } else {
        noResults.classList.remove("hidden");
      }
    }
  });
});
