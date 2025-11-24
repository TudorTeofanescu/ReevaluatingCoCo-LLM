# CoCo Analysis: dnndapinegpllfdocaogfonmcocheini

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dnndapinegpllfdocaogfonmcocheini/opgen_generated_files/bg.js
Line 988	    if (request.shop) {
	request.shop

**Code:**

```javascript
// Background script (bg.js lines 986-994):
chrome.runtime.onMessageExternal.addListener(
  function(request, sender, sendResponse) {
    if (request.shop) {
        // store shopDomain from external message
        chrome.storage.local.set({ shop: request.shop }); // ← attacker-controlled data stored
    }
    sendResponse("ok");
});

// Stored value is used to inject scripts on Aliexpress:
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && /^https:\/\/[^.\s]+\.aliexpress\.[^.\s]+/.test(tab.url)) {
        chrome.storage.local.get(["shop"]).then((result) => {
            if (result.shop) {
                chrome.scripting.executeScript({
                    target: { tabId: tabId },
                    files: ["./contentScript.js"]
                });
            }
        });
    }
});

// Also sent to hardcoded backend:
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.message === 'import') {
        chrome.storage.local.get(["shop"]).then((result) => {
            var data = request.data;
            data.shop = result.shop; // ← poisoned shop value
            send_data(data).then((res) => sendResponse(res)); // → sent to backend
        });
    }
});

function send_data(data) {
    return fetch('https://sizecharts.boutiqes.com/api/import', {
        method: 'POST',
        body: JSON.stringify(data), // ← goes to hardcoded backend
    });
}
```

**Classification:** FALSE POSITIVE

**Reason:** While external messages can poison storage via chrome.runtime.onMessageExternal (manifest restricts to https://sizecharts.boutiqes.com/* but we ignore this per methodology), this is incomplete storage exploitation. The poisoned shop value is:
1. Used to trigger script injection on Aliexpress (internal extension logic, not exploitable impact)
2. Sent to hardcoded backend URL (https://sizecharts.boutiqes.com/api/import)

Per methodology rule: "Hardcoded backend URLs are trusted infrastructure - data TO hardcoded backend is FALSE POSITIVE." There is no path where the attacker can retrieve the poisoned value back (no sendResponse with stored data, no fetch to attacker-controlled URL). Storage poisoning alone without retrieval is not exploitable.
