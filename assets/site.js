"use strict";

// The native menu works without JavaScript; Escape also returns focus to it.
const menu = document.querySelector(".mobile-menu");
if (menu) {
  menu.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && menu.open) {
      menu.open = false;
      menu.querySelector("summary").focus();
      event.preventDefault();
    }
  });
}
