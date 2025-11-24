# CoCo Analysis: mohaihianaddanfjmmclngledfmadgee

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mohaihianaddanfjmmclngledfmadgee/opgen_generated_files/bg.js
Line 980: chrome.storage.local.set({ userData: request.userData }, () => {

**Code:**

```javascript
// Background script - Entry point via onMessageExternal (line 967-982)
chrome.runtime.onMessageExternal.addListener((request, sender, sendResponse) => {
    console.log("Received external message:", request);

    if (request.action === "ping") {
        console.log("Received ping request");
        sendResponse({ status: "ok", message: "Extension is available" });
        return;
    }

    if (request.action === "startJobApplications") {
        console.log("Starting job applications for:", request.jobTitle);

        // Store the user data in local storage
        chrome.storage.local.set({ userData: request.userData }, () => { // ← Storage sink with attacker data
            console.log("User data stored:", request.userData);
        });

        // Create a new tab with the LinkedIn job search URL
        const searchUrl = `https://www.linkedin.com/jobs/search/?keywords=${encodeURIComponent(request.jobTitle)}&location=${encodeURIComponent(request.location)}`;
        chrome.tabs.create({ url: searchUrl }, (tab) => {
            // ... tab creation and message sending logic
        });
    }
});
```

**Classification:** FALSE POSITIVE

**Reason:** This is storage poisoning without a complete exploitation chain. While an attacker from whitelisted domains (https://app.scanresume.ai/* or http://localhost:3000/*) can send external messages via chrome.runtime.sendMessage() to write attacker-controlled data to storage, there is no evidence of:

1. The poisoned data being retrieved and sent back to the attacker via sendResponse or postMessage
2. The poisoned data being used in a subsequent vulnerable operation (eval, executeScript, fetch to attacker URL)

According to the methodology, "Storage poisoning alone (storage.set without retrieval) is NOT exploitable." The stored userData is passed to the content script (line 1004) which only runs on https://www.linkedin.com/*, but this is for legitimate job application automation functionality, not for sending data back to the attacker. The attacker cannot retrieve the stored data or observe its usage in a way that creates exploitable impact. Without a complete chain where the attacker can retrieve or exploit the stored values, this remains a FALSE POSITIVE.
