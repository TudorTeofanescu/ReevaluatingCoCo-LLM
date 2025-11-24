# CoCo Analysis: phmfmllkoielenbdflkockkhpphacpij

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: document_eventListener_dragstart → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/phmfmllkoielenbdflkockkhpphacpij/opgen_generated_files/cs_0.js
Line 475: document.addEventListener('dragstart', function (event) {
Line 554: const currentElement = event.target;
Line 598: let anchorElement = currentElement.closest('A');
Line 600: lastClickedLink = anchorElement.href;

**Code:**

```javascript
// Content script - cs_0.js
let lastClickedImage = null;
let lastClickedLink = null;

document.addEventListener('dragstart', function (event) {
    elementDetection(event); // Extracts image/link info
    isDroppedInsideZone = false;
    createDropZone();
});

function elementDetection(event) {
    const currentElement = event.target; // ← attacker-controlled (webpage element)
    lastClickedLink = null;

    // ... image detection logic ...

    let anchorElement = currentElement.closest('A');
    if (anchorElement) {
        lastClickedLink = anchorElement.href; // ← attacker-controlled href
    } else {
        lastClickedLink = window.location.href;
    }
}

document.addEventListener('dragend', function (event) {
    if (lastClickedImage && isDroppedInsideZone) {
        chrome.runtime.sendMessage({ // Sends to background script
            action: 'draggedItem',
            imageUrl: lastClickedImage.src, // ← attacker-controlled
            altText: lastClickedImage.alt || document.title,
            linkUrl: lastClickedLink, // ← attacker-controlled
        });
    }
});

// Background script - bg.js
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'draggedItem') {
        saveItem(message, message, message);
        sendResponse({ status: 'Item processed successfully' });
    }
    return true;
});

function saveItem(info, response, tab = {}) {
    const url = info.linkUrl || info.pageUrl || info.url; // ← attacker-controlled
    const imageUrl = response.imageUrl; // ← attacker-controlled
    const text = response.altText || tab.title;

    const item = {
        url: url,
        text: text,
        image: imageUrl,
    };

    chrome.storage.local.get('items', (data) => {
        const items = data.items || [];
        if (items.length < MAX_ITEMS) {
            items.unshift(item);
            chrome.storage.local.set({ items: items }); // Storage poisoning
        }
    });
}
```

**Classification:** FALSE POSITIVE

**Reason:** Storage poisoning only - no retrieval path to attacker. While the attacker can control image URLs and link HREFs saved to storage by dragging malicious elements on the webpage, there is no code path that retrieves this stored data and sends it back to the attacker. The stored items are only displayed in the extension's own popup UI (internal use), and cannot be accessed by external attackers.
