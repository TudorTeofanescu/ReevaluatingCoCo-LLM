# CoCo Analysis: paieegkfieiihagabeicpnghjdhpeidb

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: document_eventListener_fastEmailLogin → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/paieegkfieiihagabeicpnghjdhpeidb/opgen_generated_files/cs_1.js
Line 467: `window.document.addEventListener("fastEmailLogin", (e) => {`
Line 468: `let token = e.detail.token;`

**Code:**

```javascript
// Content script (loginContent.js) - Line 467
window.document.addEventListener("fastEmailLogin", (e) => {
    let token = e.detail.token;  // ← potentially attacker-controlled
    chrome.runtime.sendMessage({
        method: "LOGIN_SUCCESS",
        data: { accessToken: token },
    });
});

// Background script (bg.js) - Line 1097
chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
    switch (request.method) {
        case "LOGIN_SUCCESS":
            token = request.data.accessToken;
            saveToken();  // Stores to chrome.storage.sync
            sendResponse();
            break;
    }
});

// Line 1058
const saveToken = () => {
    chrome.storage.sync.set({ fastEmailAccessToken: token }, function () {
        hasToken = true;
        fetchTeams(token);
    });
};
```

**Classification:** FALSE POSITIVE

**Reason:** Storage poisoning alone without retrieval path to attacker. The content script only runs on https://app.swiftreply.net/login (developer's own domain). While the custom event listener could theoretically be triggered by an attacker on that page, the stored token is never sent back to the attacker. The extension only uses the token internally for API calls to the developer's backend, and there's no mechanism for an external attacker to retrieve the poisoned value via sendResponse, postMessage, or any other channel.
