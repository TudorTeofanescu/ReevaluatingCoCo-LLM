# CoCo Analysis: ncenkoekcinhfflcgkkjlcdibnpjabca

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: document_eventListener_contextmenu → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ncenkoekcinhfflcgkkjlcdibnpjabca/opgen_generated_files/cs_0.js
Line 485: `document.addEventListener('contextmenu', (event) => {`
Line 486: `const target = event.target;`
Line 489: `const linkUrl = target.href;`

**Analysis:**

The flow exists in the actual extension code (after line 465):
1. Line 485: Content script listens for `contextmenu` event (right-click)
2. Line 486-489: Extracts `target.href` from the clicked link element
3. Line 491: Sends the link URL to background via `chrome.runtime.sendMessage({ action: "addClipboardItem", clipboardItems: linkUrl })`
4. Background script (bg.js line 986-990): Receives message and stores in `chrome.storage.local.set({ clipboardItems: clipboardItems })`

**Code:**

```javascript
// Content script (cs_0.js) - Line 485-500
document.addEventListener('contextmenu', (event) => {
    const target = event.target; // ← Attacker can control event.target
    console.log(event.target);
    if (target.tagName === 'A' && event.button === 2) {
        const linkUrl = target.href; // ← Attacker-controlled via malicious link
        if (chrome.runtime && chrome.runtime.sendMessage) {
            chrome.runtime.sendMessage({
                action: "addClipboardItem",
                clipboardItems: linkUrl // ← Sends to background
            });
        }
    }
});

// Background script (bg.js) - Line 985-1001
function handleAddToClipboard(request, sendResponse) {
    chrome.storage.local.get(['clipboardItems']).then(result => {
        let clipboardItems = result.clipboardItems || [];
        if (!clipboardItems.includes(request.clipboardItems)) {
            clipboardItems.push(request.clipboardItems);
            return chrome.storage.local.set({ clipboardItems: clipboardItems }); // ← Storage sink
        }
    });
}
```

**Classification:** FALSE POSITIVE

**Reason:** This is storage poisoning without retrieval. The attacker can write arbitrary data to `chrome.storage.local` via right-clicking on a malicious link, but there is no exploitable path where the attacker can retrieve this stored data. The stored clipboard items are only displayed in the extension's own popup UI (not accessible to external attackers), and there's no mechanism for the attacker to read back the poisoned storage values or trigger them to be used in a vulnerable operation.
