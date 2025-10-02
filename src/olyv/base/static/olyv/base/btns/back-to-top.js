const btnBackToTop = document.querySelector("#btn_back_to_top");
btnBackToTop?.addEventListener("click", (e) => {
  e.preventDefault();
  window.scrollTo({ top: 0, behavior: "smooth" });
});

function toggleBtnVisibility() {
  if (!btnBackToTop) return;

  const shouldShow = window.scrollY > 100;
  btnBackToTop.classList.toggle("opacity-0", !shouldShow);
  btnBackToTop.classList.toggle("invisible", !shouldShow);
}

window.addEventListener("load", toggleBtnVisibility);
document.addEventListener("scroll", toggleBtnVisibility);
