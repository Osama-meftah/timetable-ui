document.addEventListener("DOMContentLoaded", () => {
  const html = document.documentElement;
  const sidebar = document.getElementById("sidebar");
  const mainContent = document.getElementById("mainContent");
  const toggleSidebarBtn = document.getElementById("toggleSidebarBtn");
  const pageTitle = document.getElementById("pageTitle");
  const navLinks = document.querySelectorAll("aside nav a");
  const darkModeToggle = document.getElementById("darkModeToggle");

  // وظيفة لتحديث عنوان الصفحة
  function updatePageTitle(title) {
    pageTitle.textContent = title;
  }

  // تعيين الرابط النشط عند التحميل الأولي (افتراضًا "لوحة التحكم")
  navLinks.forEach((link) => {
    if (link.querySelector("span").textContent === "لوحة التحكم") {
      link.classList.add("text-indigo-300", "bg-indigo-800");
      link.classList.remove("text-gray-300");
      updatePageTitle(link.querySelector("span").textContent);
    } else {
      link.classList.remove("text-indigo-300", "bg-indigo-800");
      link.classList.add("text-gray-300");
    }

    link.addEventListener("click", function (e) {
      e.preventDefault(); // منع الانتقال الفعلي للصفحة لتجربة الواجهة

      // إزالة الحالة النشطة من جميع الروابط
      navLinks.forEach((item) => {
        item.classList.remove("text-indigo-300", "bg-indigo-800");
        item.classList.add("text-gray-300");
      });

      // إضافة الحالة النشطة للرابط الذي تم النقر عليه
      this.classList.add("text-indigo-300", "bg-indigo-800");
      this.classList.remove("text-gray-300");

      // تحديث عنوان الصفحة
      updatePageTitle(this.querySelector("span").textContent);
    });
  });

  // إضافة المستمع لزر الطي/التوسيع
  if (toggleSidebarBtn) {
    toggleSidebarBtn.addEventListener("click", () => {
      sidebar.classList.toggle("sidebar-collapsed");
      mainContent.classList.toggle("main-content-collapsed");
    });
  }

  // --- فلترة الجدول الشامل ---
  const filterCourse = document.getElementById("filter_course");
  const filterTeacher = document.getElementById("filter_teacher");
  const filterRoom = document.getElementById("filter_room");
  const filterLevel = document.getElementById("filter_level");
  const fullScheduleTableBody = document.querySelector(
    "#fullScheduleTable tbody"
  );
  const allRows = Array.from(fullScheduleTableBody.querySelectorAll("tr"));

  function applyFilters() {
    const selectedCourse = filterCourse.value;
    const selectedTeacher = filterTeacher.value;
    const selectedRoom = filterRoom.value;
    const selectedLevel = filterLevel.value;

    allRows.forEach((row) => {
      const course = row.dataset.course;
      const teacher = row.dataset.teacher;
      const room = row.dataset.room;
      const level = row.dataset.level;

      const matchesCourse = selectedCourse === "" || course === selectedCourse;
      const matchesTeacher =
        selectedTeacher === "" || teacher === selectedTeacher;
      const matchesRoom = selectedRoom === "" || room === selectedRoom;
      const matchesLevel = selectedLevel === "" || level === selectedLevel;

      if (matchesCourse && matchesTeacher && matchesRoom && matchesLevel) {
        row.style.display = ""; // Show row
      } else {
        row.style.display = "none"; // Hide row
      }
    });
  }

  // Add event listeners to filters
  filterCourse.addEventListener("change", applyFilters);
  filterTeacher.addEventListener("change", applyFilters);
  filterRoom.addEventListener("change", applyFilters);
  filterLevel.addEventListener("change", applyFilters);

  // Initial filter application in case default values are set
  applyFilters();

  // --- Dark Mode Logic ---
  // Set initial theme based on localStorage or system preference
  const currentTheme = localStorage.getItem("theme");
  if (currentTheme === "dark") {
    html.classList.add("dark");
    html.classList.remove("light");
    darkModeToggle.checked = true;
  } else if (currentTheme === "light") {
    html.classList.add("light");
    html.classList.remove("dark");
    darkModeToggle.checked = false;
  } else if (
    window.matchMedia &&
    window.matchMedia("(prefers-color-scheme: dark)").matches
  ) {
    // If no preference is set in localStorage, check system preference
    html.classList.add("dark");
    darkModeToggle.checked = true;
  } else {
    html.classList.add("light");
    darkModeToggle.checked = false;
  }

  // Add event listener for the dark mode toggle
  darkModeToggle.addEventListener("change", () => {
    if (darkModeToggle.checked) {
      html.classList.remove("light");
      html.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      html.classList.remove("dark");
      html.classList.add("light");
      localStorage.setItem("theme", "light");
    }
  });
});
