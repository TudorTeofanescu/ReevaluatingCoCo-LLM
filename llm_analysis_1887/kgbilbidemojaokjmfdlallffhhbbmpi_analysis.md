# CoCo Analysis: kgbilbidemojaokjmfdlallffhhbbmpi

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kgbilbidemojaokjmfdlallffhhbbmpi/opgen_generated_files/bg.js
Line 1088: request.payload
from bg_chrome_runtime_MessageExternal to chrome_storage_local_set_sink
```

**Code:**
```javascript
// Background script - Line 1086
chrome.runtime.onMessageExternal.addListener((request, sender, sendResponse) => {
  if (request.hasOwnProperty('type') && request.type === 'authData') {
    chrome.storage.local.set({ authData: request.payload }, () => {
      // ← attacker from senseai.online can control request.payload
      console.log('Received auth data from web app');
    });
  }
});

// Line 1011 - Storage retrieval
chrome.storage.local.get(['authData'], function (result) {
  if (
    result &&
    result.hasOwnProperty('authData') &&
    result.authData.hasOwnProperty('access_token') &&
    result.authData.hasOwnProperty('organization_id')
  ) {
    request = {
      headers: {
        Authorization: 'Bearer ' + result.authData.access_token, // ← attacker-controlled
        'X-Org-Id': result.authData.organization_id, // ← attacker-controlled
      },
    };
  }
});

// Line 1008 - Hardcoded backend URL
const gatewayUrl = 'https://senseai.online/gateway/ai-service'; // ← trusted infrastructure
```

**Classification:** FALSE POSITIVE

**Reason:** Hardcoded backend URL (trusted infrastructure). While the manifest's `externally_connectable` allows senseai.online domain to send messages that poison storage with arbitrary authData, the poisoned data is only retrieved and sent to the extension's own hardcoded backend server `https://senseai.online/gateway/ai-service`. The flow is:
1. Attacker (senseai.online page) → onMessageExternal → storage.set(authData)
2. Storage.get(authData) → used in headers for fetch to hardcoded `gatewayUrl = 'https://senseai.online/gateway/ai-service'`

According to the methodology, data sent to hardcoded developer backend URLs is FALSE POSITIVE, as compromising developer infrastructure is separate from extension vulnerabilities.
