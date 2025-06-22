/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: [
    "./templates/**/*.html", // قوالب Django
    "./**/*.py", // ملفات البايثون (للحالات الخاصة)
    "./static/**/*.js",
    "./**/templates/**/*.html",
    // إذا كان لديك أي JavaScript في مجلدات 'static' داخل التطبيقات
    "./**/static/**/*.js",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
