# CoCo Analysis: bjdkhikjbkefnnfkaghgeejggggplfbi

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2 (chrome_storage_local_set_sink)

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bjdkhikjbkefnnfkaghgeejggggplfbi/opgen_generated_files/cs_1.js
Line 519: window.addEventListener('message', function(event) {
Line 525: if (event.data.name === 'activate')
Line 505: if (typeof event.data.user_id === 'string' && typeof event.data.token === 'string')

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bjdkhikjbkefnnfkaghgeejggggplfbi/opgen_generated_files/bg.js
Line 1069: chrome.storage.local.set(data, ...)

**Code:**

```javascript
// Content script - Entry point (cs_1.js, Line 519)
window.addEventListener('message', function(event) {
    // Only accept messages from activation page
    if (event.source !== window) {
      return;
    }

    if (event.data.name === 'activate') {
      activate(event); // ← calls activate with attacker-controlled event
    } else if (event.data.name === 'deactivate') {
      deactivate();
    }
  }, false);

function activate(event) {
  if (typeof event.data.user_id === 'string' && typeof event.data.token === 'string') {
    sendMessage('setStorage', { user_id: event.data.user_id, token: event.data.token }); // ← attacker-controlled
  }
}

function sendMessage(name, message) {
  if (isWebExtension) {
    chrome.runtime.sendMessage({ name: name, message: message });
  }
}

// Background script - Message handler (bg.js, Line 1103-1107)
function handleBackgroundMessage(event, sender) {
  if (event.name === 'getStorage') {
    getStorage(event.message, sender || event);
  } else if (event.name === 'setStorage') {
    setStorage(event.message, sender || event); // ← receives attacker data
  } else if (event.name === 'clearStorage') {
    clearStorage(event, sender || event);
  }
}

function setStorage(data, eventOrSender) {
  if (isWebExtension) {
    chrome.storage.local.set(data, function() { // ← stores attacker data
      if (chrome.runtime.lastError) {
        sendMessage('setStorageResult', { message: data, error: chrome.runtime.lastError }, eventOrSender);
      } else {
        sendMessage('setStorageResult', data, eventOrSender);
      }
    });
  }
}

// Retrieval function exists but webpage cannot trigger it
function getStorage(key, eventOrSender) {
  if (isWebExtension) {
    chrome.storage.local.get(key, function(data) {
      sendMessage('getStorageResult', data, eventOrSender); // Sends data back
    });
  }
}

chrome.runtime.onMessage.addListener(handleBackgroundMessage);
```

**Classification:** FALSE POSITIVE

**Reason:** Incomplete storage exploitation chain. While the attacker can poison storage by sending `window.postMessage({name: 'activate', data: {user_id: 'X', token: 'Y'}}, '*')`, there is no way to retrieve the stored values back. The content script only accepts 'activate' and 'deactivate' messages from postMessage (Line 525-528), not 'getStorage'. The getStorage function exists and would send data back via sendMessage, but the webpage cannot trigger it through postMessage. The handleBackgroundMessage response (setStorageResult) only sets a dataset attribute (Line 481-482) indicating activation status, not the actual poisoned values. Per methodology rule: "Storage poisoning alone is NOT a vulnerability - the stored value MUST flow back to the attacker through sendResponse, postMessage, or be used in a subsequent vulnerable operation to be TRUE POSITIVE."
