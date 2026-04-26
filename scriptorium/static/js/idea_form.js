/*
static/js/idea_form.js
Comportamiento menor para formulario de ideas.
Arquitectura: Views/Frontend JS.
*/

document.addEventListener("DOMContentLoaded", () => {
  const textarea = document.querySelector("textarea[name=text]");
  if (!textarea) return;
  textarea.addEventListener("input", () => {
    const counter = document.getElementById("ideaCharCount");
    if (counter) {
      const length = textarea.value.length;
      counter.textContent = String(length);
      
      if (length > 0 && length < 30) {
        counter.style.color = "#f59e0b"; // Naranja (muy corto)
      } else if (length >= 30) {
        counter.style.color = "#10b981"; // Verde (buen desarrollo)
      } else {
        counter.style.color = "inherit";
      }
    }
  });
});
