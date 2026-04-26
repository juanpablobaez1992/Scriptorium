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
    if (counter) counter.textContent = String(textarea.value.length);
  });
});
