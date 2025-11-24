# CoCo Analysis: mpaohidlipnfnkbogpmanchjfjpdgcml

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → chrome_downloads_download_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mpaohidlipnfnkbogpmanchjfjpdgcml/opgen_generated_files/cs_0.js
Line 599     window.addEventListener('message', function (event) {
Line 600     if (event.data.type && event.data.type === 'ankileo.download') {

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mpaohidlipnfnkbogpmanchjfjpdgcml/opgen_generated_files/bg.js
Line 1138    var resultBlob = new Blob(arg.payload.data, {
Line 1144    filename: arg.payload.name
```

**Code:**

```javascript
// Content script - Only on lingualeo.com domain (cs_0.js Line 599)
window.addEventListener('message', function (event) {
  if (event.data.type && event.data.type === 'ankileo.download') {
    chrome.runtime.sendMessage(event.data);
  }
}, false);

// Background script (bg.js Line 1136)
chrome.runtime.onMessage.addListener(function (arg) {
  if (arg.type && arg.type === 'ankileo.download') {
    var resultBlob = new Blob(arg.payload.data, {
      type: 'text/csv;charset=utf-8'
    });
    var url = URL.createObjectURL(resultBlob);
    chrome.downloads.download({
      url: url,
      filename: arg.payload.name
    });
  }
});
```

**Classification:** FALSE POSITIVE

**Reason:** The content script only runs on lingualeo.com domain (as specified in manifest.json: "matches":["*://lingualeo.com/*"]). The extension is designed to work exclusively with the legitimate Lingualeo language learning website to export vocabulary data. While technically the webpage could send arbitrary download commands, this is the intended functionality - allowing users to download their vocabulary data from Lingualeo. The attacker would need to compromise lingualeo.com itself, which falls outside the threat model as it represents trusted infrastructure for this extension's purpose. Additionally, the download only creates a Blob from provided data (CSV export), not arbitrary file downloads from attacker-controlled URLs.
