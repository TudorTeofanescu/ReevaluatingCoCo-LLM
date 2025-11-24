# CoCo Analysis: mpaohidlipnfnkbogpmanchjfjpdgcml

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → chrome_downloads_download_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mpaohidlipnfnkbogpmanchjfjpdgcml/opgen_generated_files/cs_0.js
Line 599	window.addEventListener('message', function (event) {
Line 600	  if (event.data.type && event.data.type === 'ankileo.download') {

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mpaohidlipnfnkbogpmanchjfjpdgcml/opgen_generated_files/bg.js
Line 1138	    var resultBlob = new Blob(arg.payload.data, {
Line 1144	      filename: arg.payload.name
```

**Code:**

```javascript
// Content script (cs_0.js) - Entry point at line 599
window.addEventListener('message', function (event) {
  if (event.data.type && event.data.type === 'ankileo.download') {
    chrome.runtime.sendMessage(event.data); // ← attacker-controlled event.data
  }
}, false);

// Background script (bg.js) - Message handler at line 1136
chrome.runtime.onMessage.addListener(function (arg) {
  if (arg.type && arg.type === 'ankileo.download') {
    var resultBlob = new Blob(arg.payload.data, { // ← attacker-controlled data
      type: 'text/csv;charset=utf-8'
    });
    var url = URL.createObjectURL(resultBlob);
    chrome.downloads.download({
      url: url,
      filename: arg.payload.name // ← attacker-controlled filename
    });
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from malicious webpage

**Attack:**

```javascript
// Malicious webpage can inject content script into lingualeo.com domain
// and send arbitrary download request
window.postMessage({
  type: 'ankileo.download',
  payload: {
    data: ['malicious content'],
    name: 'malware.exe' // ← arbitrary filename
  }
}, '*');
```

**Impact:** An attacker on lingualeo.com can trigger arbitrary file downloads with attacker-controlled filename and content. The extension listens for window messages without validating the origin, allowing any webpage on lingualeo.com to trigger downloads. While the content script is only injected on lingualeo.com (per manifest content_scripts matches), an attacker who controls or compromises that domain can exploit this vulnerability. The extension has the "downloads" permission in manifest.json, making this attack fully executable.
