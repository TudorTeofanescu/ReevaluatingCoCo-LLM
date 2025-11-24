# CoCo Analysis: omojidakhdcgakihbljcgijdiooihnhg

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/omojidakhdcgakihbljcgijdiooihnhg/opgen_generated_files/bg.js
Line 1009: `chrome.storage.local.set({ "authToken": request.res });`

**Code:**

```javascript
// Background script - External message handler (bg.js Line 1006-1029)
chrome.runtime.onMessageExternal.addListener(
    function(request, sender, sendResponse) {
        if (request.action === "updateAuth") {
            chrome.storage.local.set({ "authToken": request.res });  // Storage write

            firebase.auth().signInWithCustomToken(request.res)  // Token validated by Firebase
            .then((userCredential) => {
                const user = userCredential.user;
                chrome.runtime.sendMessage({ action: "loginSuccess", user });
                chrome.storage.local.set({ "isLoggedIn": true });
                sendResponse({ success: true });
            })
            .catch((error) => {
                console.error("Authentication error:", error.message);
                sendResponse({ success: false, error: error.message });
            });
            return true;
        }
    }
);
```

**Classification:** FALSE POSITIVE

**Reason:** Storage poisoning alone without retrieval path. While external messages can write arbitrary auth tokens to storage, there's no exploitable impact. The token is immediately validated by Firebase (trusted backend), and invalid tokens will fail authentication. No evidence of the stored token flowing back to the attacker via sendResponse, postMessage, or being used in attacker-controlled operations.
