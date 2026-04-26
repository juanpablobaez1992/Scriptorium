/*
static/js/filters.js
Utilidades simples de filtros para vistas.
Arquitectura: Views/Frontend JS.
*/

document.addEventListener("DOMContentLoaded", () => {
  const autoSubmitForms = document.querySelectorAll("[data-auto-submit=true]");
  autoSubmitForms.forEach((el) => {
    el.addEventListener("change", () => {
      if (el.form) {
        el.style.opacity = "0.5";
        el.style.pointerEvents = "none";
        el.form.submit();
      }
    });
  });
});
