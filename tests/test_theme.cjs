"use strict";

const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const script = readFileSync(path.join(__dirname, "../assets/site.js"), "utf8");
const KEY = "meeting-pulse-trust-theme";

function events(target = {}) {
  const listeners = new Map();
  target.addEventListener = (type, callback) => {
    if (!listeners.has(type)) listeners.set(type, []);
    listeners.get(type).push(callback);
  };
  target.emit = (type, event = {}) => {
    for (const callback of listeners.get(type) || []) callback(event);
  };
  return target;
}

function setup({ dark = false, saved = null, blockedRead = false, blockedWrite = false } = {}) {
  const values = new Map(saved === null ? [] : [[KEY, saved]]);
  let writes = 0;
  const storage = {
    getItem(key) {
      if (blockedRead) throw new Error("Storage blocked");
      return values.get(key) ?? null;
    },
    setItem(key, value) {
      if (blockedWrite) throw new Error("Storage full");
      writes += 1;
      values.set(key, value);
    },
    removeItem(key) {
      if (blockedWrite) throw new Error("Storage blocked");
      writes += 1;
      values.delete(key);
    },
  };
  const media = events({ matches: dark });
  const window = events({ localStorage: storage, matchMedia: () => media });
  const controls = { hidden: true };
  const buttons = ["system", "light", "dark"].map((choice) => events({
    dataset: { themeChoice: choice },
    attributes: {},
    setAttribute(key, value) { this.attributes[key] = value; },
  }));
  let focused = false;
  const menu = events({ open: true, querySelector: () => ({ focus() { focused = true; } }) });
  let ready = false;
  const document = events({
    documentElement: { dataset: {} },
    querySelectorAll: () => ready ? buttons : [],
    querySelector: (selector) => selector === ".theme-switcher" ? controls : menu,
  });
  vm.runInNewContext(script, { window, document });
  const beforeDOM = document.documentElement.dataset.theme;
  ready = true;
  document.emit("DOMContentLoaded");
  return {
    beforeDOM, controls, storage, window, buttons, menu,
    theme: () => document.documentElement.dataset.theme,
    saved: () => values.get(KEY),
    writes: () => writes,
    focused: () => focused,
    pressed: () => buttons.filter((b) => b.attributes["aria-pressed"] === "true")
      .map((b) => b.dataset.themeChoice),
    click(choice) { buttons.find((b) => b.dataset.themeChoice === choice).emit("click"); },
    changeDevice(value) { media.matches = value; media.emit("change"); },
    storageEvent(value, area = storage, current = value) {
      if (area === storage) {
        if (current === null) values.delete(KEY);
        else values.set(KEY, current);
      }
      window.emit("storage", { key: KEY, newValue: value, storageArea: area });
    },
  };
}

test("defaults to light before the DOM when the device is light", () => {
  const page = setup();
  assert.equal(page.beforeDOM, "light");
  assert.equal(page.theme(), "light");
  assert.equal(page.writes(), 0);
  assert.deepEqual(page.pressed(), ["system"]);
  assert.equal(page.controls.hidden, false);
});

test("defaults to dark before the DOM when the device is dark", () => {
  const page = setup({ dark: true });
  assert.equal(page.beforeDOM, "dark");
  assert.equal(page.theme(), "dark");
});

test("follows device changes while in System mode", () => {
  const page = setup();
  page.changeDevice(true);
  assert.equal(page.theme(), "dark");
  page.changeDevice(false);
  assert.equal(page.theme(), "light");
  assert.equal(page.writes(), 0);
});

for (const choice of ["light", "dark"]) {
  test("restores saved " + choice + " before the DOM regardless of device changes", () => {
    const page = setup({ saved: choice, dark: choice === "light" });
    assert.equal(page.beforeDOM, choice);
    page.changeDevice(choice !== "light");
    assert.equal(page.theme(), choice);
    assert.deepEqual(page.pressed(), [choice]);
  });
  test("persists a manual " + choice + " choice across page loads", () => {
    const page = setup({ dark: choice === "light" });
    page.click(choice);
    assert.equal(page.theme(), choice);
    assert.equal(page.saved(), choice);
    assert.deepEqual(page.pressed(), [choice]);
    assert.equal(setup({ saved: page.saved() }).theme(), choice);
  });
}

test("System clears the saved override and resumes device changes", () => {
  const page = setup({ saved: "light", dark: true });
  page.click("system");
  assert.equal(page.saved(), undefined);
  assert.equal(page.theme(), "dark");
  assert.deepEqual(page.pressed(), ["system"]);
  page.changeDevice(false);
  assert.equal(page.theme(), "light");
});

test("ignores unknown stored values", () => {
  const page = setup({ saved: "unexpected", dark: true });
  assert.equal(page.theme(), "dark");
  assert.deepEqual(page.pressed(), ["system"]);
});

test("blocked storage reads do not break theme selection", () => {
  const page = setup({ blockedRead: true, dark: true });
  assert.equal(page.theme(), "dark");
  page.click("light");
  assert.equal(page.theme(), "light");
});

test("blocked storage writes do not break theme selection", () => {
  const page = setup({ blockedWrite: true });
  page.click("dark");
  assert.equal(page.theme(), "dark");
  page.click("system");
  assert.equal(page.theme(), "light");
});

test("synchronizes a changed preference from another tab", () => {
  const page = setup();
  page.storageEvent("dark");
  assert.equal(page.theme(), "dark");
  assert.deepEqual(page.pressed(), ["dark"]);
  page.storageEvent(null);
  assert.equal(page.theme(), "light");
  assert.deepEqual(page.pressed(), ["system"]);
});

test("ignores storage changes from another storage area", () => {
  const page = setup();
  page.storageEvent("dark", {});
  assert.equal(page.theme(), "light");
});

test("a queued storage event reconciles the latest saved preference", () => {
  const page = setup();
  page.storageEvent("dark", page.storage, "light");
  assert.equal(page.theme(), "light");
  assert.equal(page.saved(), "light");
  assert.deepEqual(page.pressed(), ["light"]);
});

test("clearing local storage restores automatic theme", () => {
  const page = setup({ saved: "light", dark: true });
  page.storage.removeItem(KEY);
  page.window.emit("storage", { key: null, newValue: null, storageArea: page.storage });
  assert.equal(page.theme(), "dark");
  assert.deepEqual(page.pressed(), ["system"]);
});

test("Escape still closes the mobile menu and returns focus", () => {
  const page = setup();
  let prevented = false;
  page.menu.emit("keydown", { key: "Escape", preventDefault() { prevented = true; } });
  assert.equal(page.menu.open, false);
  assert.equal(page.focused(), true);
  assert.equal(prevented, true);
});
