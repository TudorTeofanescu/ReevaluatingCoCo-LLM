# CoCo Analysis: eppfflbpkkdncjjlhnifngdkdbeljonf

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/eppfflbpkkdncjjlhnifngdkdbeljonf/opgen_generated_files/bg.js
Line 1023: `if (request.jwt) {`

**Code:**

```javascript
// Background script
const API_LOGIN = "https://api.gptcase.show/connect/google";
const API_CONVERSATIONS = "https://api.gptcase.show/conversations";

// Step 1: External message stores JWT
chrome.runtime.onMessageExternal.addListener(
  (request, sender, sendResponse) => {
    // login jwt
    if (request.jwt) {
      chrome.storage.sync.set({ "gptcase-jwt": request.jwt }).then(() => {
        console.log("GPTCase Login");
      });
    }
  }
);

// Step 2: JWT is retrieved and sent to hardcoded backend
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "share") {
    chrome.storage.sync
      .get(["gptcase-jwt"])
      .then(({ "gptcase-jwt": token }) => {
        // Send a POST request to the conversations endpoint with the chat data and the token as headers
        fetch(API_CONVERSATIONS, { // ← hardcoded backend
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}` // JWT sent to hardcoded backend
          },
          body: JSON.stringify(request.chat),
        })
        // ... response handling
      });
  }
});
```

**Classification:** FALSE POSITIVE

**Reason:** While external messages can poison the storage with a malicious JWT (via chrome.runtime.onMessageExternal from whitelisted domain gptcase.show), the retrieval path sends the stored JWT to a hardcoded backend (https://api.gptcase.show/conversations). This falls under the "Storage to hardcoded backend" false positive pattern. The flow is: external message → storage.set → storage.get → fetch(hardcodedBackend). Sending attacker-controlled data to the developer's own backend is not an extension vulnerability; it's a trusted infrastructure issue. The attacker cannot retrieve the poisoned JWT back or use it in any exploitable operation within the extension's privilege context.
