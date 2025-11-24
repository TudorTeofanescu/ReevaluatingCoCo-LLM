# CoCo Analysis: dmcfhbnmfaadjefaainadmhgdoclnncc

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: document_body_innerText → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dmcfhbnmfaadjefaainadmhgdoclnncc/opgen_generated_files/cs_0.js
Line 480: `let countword=countWords(document.body.innerText.replace(/(<([^>]+)>)/gi, ""));`
Line 599-600: `var words = request.split(/\s+/); return words.length;`

**Code:**

```javascript
// Content script - Triggered by visibility change (internal browser event)
document.onvisibilitychange = async function() {
    await visibilitychaged();
};

async function visibilitychaged(){
    const item = await chrome.storage.sync.get(['paidforRead']);
    paidforRead = item.paidforRead;
    let countword=countWords(document.body.innerText.replace(/(<([^>]+)>)/gi, ""));
    chrome.storage.sync.set({ countword }); // Stores word count
}

function countWords(request) {
    var words = request.split(/\s+/);
    return words.length;
}
```

**Classification:** FALSE POSITIVE

**Reason:** No external attacker trigger. The flow is triggered by the `visibilitychange` event, which is an internal browser event that occurs when the user switches tabs or minimizes the window. This is not controllable by external attackers. The extension simply reads page content (document.body.innerText) and stores a word count in chrome.storage.sync - this is legitimate extension functionality with no exploitable attack path.
