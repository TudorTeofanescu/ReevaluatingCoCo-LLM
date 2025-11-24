# CoCo Analysis: eiifniieamgecanhcjlachkbefeflifa

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 3

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (token)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/eiifniieamgecanhcjlachkbefeflifa/opgen_generated_files/bg.js
Line 992: `if (request.token) {`
Line 994: `fairwaiToken: request.token,`

**Code:**

```javascript
// Background - External message listener (bg.js Line 986)
chrome.runtime.onMessageExternal.addListener(function (request, sender, sendResponse) {
    if (request.function === "tokenFairwai") {
        if (request.token) {
            chrome.storage.local.set({
                fairwaiToken: request.token, // ← attacker-controlled (Sink 1)
                username: request.username,  // ← attacker-controlled (Sink 3)
                userEmail: request.userMail, // ← attacker-controlled (Sink 2)
            });
        }
        sendResponse({ ok: true }); // Static response only
    }
});

// The stored token is later retrieved and sent to hardcoded backend
async function getFairwaiDocumentsFromCollection(collectionId) {
    token = await getKeyFromLocalStorage("fairwaiToken");
    url = baseUrl + "/api/documents.list"; // baseUrl = "https://app.fairw.ai" (hardcoded)

    options = {
        method: "POST",
        headers: {
            Authorization: "Bearer " + token, // Poisoned token sent to developer's backend
        },
        body: JSON.stringify(params),
    };

    return fetch(url, options); // Goes to trusted infrastructure, not attacker
}
```

**Classification:** FALSE POSITIVE

**Reason:** Hardcoded backend URL (trusted infrastructure). The extension accepts external messages and stores attacker-controlled token, username, and userEmail. However, the stored data is only sent to the hardcoded backend URL `https://app.fairw.ai`, which is the developer's trusted infrastructure. The attacker cannot retrieve the poisoned data back via sendResponse (only returns static `{ ok: true }`). According to the methodology, data sent to/from hardcoded developer backend URLs is considered trusted infrastructure, not an extension vulnerability. Compromising developer infrastructure is a separate issue from extension vulnerabilities.

---

## Sink 2: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (userEmail)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/eiifniieamgecanhcjlachkbefeflifa/opgen_generated_files/bg.js
Line 992: `if (request.token) {`
Line 996: `userEmail: request.userMail,`

**Classification:** FALSE POSITIVE

**Reason:** Same as Sink 1 - stored data only flows to hardcoded backend URL (trusted infrastructure), not back to attacker.

---

## Sink 3: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (username)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/eiifniieamgecanhcjlachkbefeflifa/opgen_generated_files/bg.js
Line 992: `if (request.token) {`
Line 995: `username: request.username,`

**Classification:** FALSE POSITIVE

**Reason:** Same as Sink 1 - stored data only flows to hardcoded backend URL (trusted infrastructure), not back to attacker.
