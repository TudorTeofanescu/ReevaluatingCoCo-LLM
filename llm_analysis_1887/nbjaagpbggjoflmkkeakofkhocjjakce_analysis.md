# CoCo Analysis: nbjaagpbggjoflmkkeakofkhocjjakce

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1 (bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink)

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nbjaagpbggjoflmkkeakofkhocjjakce/opgen_generated_files/bg.js
Line 1007: chrome.storage.local.set({ auth_token: request.auth_token });

**Code:**

```javascript
// Background script (Lines 1004-1019)
chrome.runtime.onMessageExternal.addListener(function (request, sender, sendResponse) {
  console.log("Sender " + sender.url);
  console.log(request);
  chrome.storage.local.set({ auth_token: request.auth_token }); // Storage poisoning

  if (request.auth_token) {
    if (isTokenExpired(request.auth_token || request.auth_token === null)) {
      clearAllData();
    } else {
      chrome.storage.local.set({ auth_token: request.auth_token }, function () {
        console.log("Auth token stored:");
      });
    }
  } else {
    clearAllData();
  }
});

// Later retrieval and use (Lines 1100-1115)
chrome.storage.local.get(['auth_token'], function(result) {
  if (!result.auth_token || isTokenExpired(result.auth_token)) {
    clearAllData();
    reject(new Error("Authentication token is missing or expired"));
    return;
  }

  const apiUrl = `${config.scanAPI}?url=${encodeURIComponent(scholarshipUrl)}`;

  fetch(apiUrl, {  // config.scanAPI = "https://api.scholarbox.org/api/Eligibility/CheckEligibility"
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${result.auth_token}`,  // Token sent to hardcoded backend
      'Content-Type': 'application/json'
    }
  })
  // ...
});
```

**Manifest Configuration:**
```json
{
  "externally_connectable": {
    "matches": [
      "https://scholarbox.org/*",
      "https://qa.scholarbox.org/*",
      "http://localhost:3000/*",
      "https://localhost:3000/*"
    ]
  }
}
```

**Classification:** FALSE POSITIVE

**Reason:** Incomplete storage exploitation. While the extension allows external messages to set auth_token in storage (storage poisoning), the stored token is only sent to the hardcoded developer backend URL (https://api.scholarbox.org/api/Eligibility/CheckEligibility). Per methodology: "Storage to hardcoded backend: storage.get → fetch(hardcodedBackendURL) = FALSE POSITIVE. Developer trusts their own infrastructure; compromising it is infrastructure issue, not extension vulnerability." The attacker cannot retrieve the poisoned token back, and it only goes to trusted infrastructure.
