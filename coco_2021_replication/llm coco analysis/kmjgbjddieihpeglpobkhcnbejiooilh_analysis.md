# CoCo Analysis: kmjgbjddieihpeglpobkhcnbejiooilh

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1 (cs_window_eventListener_PassAccessToken → chrome_storage_local_set_sink)

---

## Sink 1: cs_window_eventListener_PassAccessToken → chrome_storage_local_set_sink

**CoCo Trace:**
```
$FilePath$/media/data2/jianjia/extension_data/unzipped_extensions/kmjgbjddieihpeglpobkhcnbejiooilh/opgen_generated_files/cs_0.js
Line 676: window.addEventListener("PassAccessToken", function (evt) {
Line 677: chrome.storage.local.set({ accessToken: evt.detail });
```

**Code:**

```javascript
// Content script (cs_0.js) - runs on https://app.snapp.taxi/*
function injectScript(file_path, tag) {
    var node = document.getElementsByTagName(tag)[0];
    var script = document.createElement("script");
    script.setAttribute("type", "text/javascript");
    script.setAttribute("src", file_path);
    node.appendChild(script);
}

injectScript(chrome.runtime.getURL("assets/getAccessToken.js"), "body");

window.addEventListener("PassAccessToken", function (evt) {
    chrome.storage.local.set({ accessToken: evt.detail }); // ← stores token from event
}, false);
```

**Classification:** FALSE POSITIVE

**Reason:** This is NOT an external attacker-controlled vector. The custom DOM event "PassAccessToken" is dispatched by the extension's own injected script (getAccessToken.js), which is a web-accessible resource loaded from the extension itself. This is internal communication between the extension's injected page script and content script to extract the access token from the Snapp app page. The event is NOT triggered by the webpage or external attacker - it's triggered by the extension's own code. This is a legitimate pattern for content script ↔ page script communication within the same extension. The extension only runs on https://app.snapp.taxi/*, and the token extraction is the intended functionality for analyzing Snapp rides.
