"use strict";

(() => {
  const key = "meeting-pulse-trust-theme";
  const device = window.matchMedia("(prefers-color-scheme: dark)");
  let preference = "system";
  let storage = null;

  const validPreference = (value) =>
    value === "light" || value === "dark" ? value : "system";

  try {
    storage = window.localStorage;
    preference = validPreference(storage.getItem(key));
  } catch {
    storage = null;
  }

  function applyTheme() {
    document.documentElement.dataset.theme = preference === "system"
      ? (device.matches ? "dark" : "light") : preference;
    document.querySelectorAll("[data-theme-choice]").forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.themeChoice === preference));
    });
  }

  // This script runs before CSS so saved overrides apply before the first paint.
  applyTheme();
  device.addEventListener("change", applyTheme);
  window.addEventListener("storage", (event) => {
    if (storage && event.storageArea === storage && (event.key === key || event.key === null)) {
      try {
        // Another tab may have saved a newer choice while this event was queued.
        preference = validPreference(storage.getItem(key));
      } catch {
        return;
      }
      applyTheme();
    }
  });

  document.addEventListener("DOMContentLoaded", () => {
    const controls = document.querySelector(".theme-switcher");
    if (controls) {
      document.querySelectorAll("[data-theme-choice]").forEach((button) => {
        button.addEventListener("click", () => {
          preference = validPreference(button.dataset.themeChoice);
          try {
            if (preference === "system") storage?.removeItem(key);
            else storage?.setItem(key, preference);
          } catch {
            // The theme still works when browser storage is unavailable or full.
          }
          applyTheme();
        });
      });
      applyTheme();
      controls.hidden = false;
    }

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
  });
})();
