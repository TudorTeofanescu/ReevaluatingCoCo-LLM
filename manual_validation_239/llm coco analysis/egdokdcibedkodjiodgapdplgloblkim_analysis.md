# CoCo Analysis: egdokdcibedkodjiodgapdplgloblkim

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 9 (all chrome_storage_local_set_sink)

---

## Sink 1-9: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/egdokdcibedkodjiodgapdplgloblkim/opgen_generated_files/cs_1.js
Line 479: window.addEventListener("message", function (event) {
Line 485: if (event.data.hasOwnProperty('type') && (event.data.type === "EXTENSION_CHECK")) {

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/egdokdcibedkodjiodgapdplgloblkim/opgen_generated_files/bg.js
Line 1024: "notificationId": request.session,

**Code:**

```javascript
// Content script - Entry point (cs_1.js)
window.addEventListener("message", function (event) {
    if (event.source !== window) {
        return;
    }

    if (event.data.hasOwnProperty('type') && (event.data.type === "CALL_MANAGEMENT")) {
        chrome.runtime.sendMessage(event.data);  // <- forwards entire event.data
    }
});

// Background script - Message handler (bg.js)
chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
    if (request.type === 'CALL_MANAGEMENT') {
        if (request.call_type === 'incoming') {
            if (request.state === 'ringing') {
                chrome.storage.local.get(["peopsoft"], function (result) {
                    result.peopsoft[request.session] = {  // <- request.session is attacker-controlled (used as key)
                        "notificationId": request.session,  // <- attacker-controlled
                        "windowsId": sender.tab.windowId,   // <- browser-set, NOT attacker-controlled
                        "tabId": sender.tab.id,             // <- browser-set, NOT attacker-controlled
                        "type": 1
                    };
                    chrome.storage.local.set({
                        "peopsoft": result.peopsoft
                    });
                });

                chrome.notifications.create(request.session, {
                    type: "basic",
                    requireInteraction: true,
                    silent: true,
                    iconUrl: "img/icon_128.png",
                    title: request.display_title,      // <- attacker-controlled
                    message: request.display_message,  // <- attacker-controlled
                    contextMessage: request.display_context,  // <- attacker-controlled
                    buttons: [{
                        title: request.b1_titel  // <- attacker-controlled
                    }, {
                        title: request.b2_titel  // <- attacker-controlled
                    }]
                });
            }
        }
    }
});

// Storage retrieval - NOT exploitable
chrome.notifications.onClicked.addListener(function (notificationId) {
    chrome.storage.local.get(["peopsoft"], function (result) {
        if (result.peopsoft.hasOwnProperty(notificationId)) {
            // Uses stored values, but windowsId and tabId are browser-set
            chrome.windows.update(result.peopsoft[notificationId]["windowsId"], { "focused": true });
            chrome.tabs.update(result.peopsoft[notificationId]["tabId"], { "active": true });
        }
    });
});

chrome.notifications.onButtonClicked.addListener(function (notificationId, buttonIndex) {
    chrome.storage.local.get(["peopsoft"], function (result) {
        if (result.peopsoft.hasOwnProperty(notificationId)) {
            let message = {
                type: 'ACTION',
                sessionId: notificationId,
                action: 'terminate'
            };
            // Sends message to stored tabId, but tabId is browser-set
            chrome.tabs.sendMessage(result.peopsoft[notificationId]["tabId"], message);
        }
    });
});
```

**Classification:** FALSE POSITIVE

**Reason:** Storage poisoning without exploitable retrieval path. While the attacker can control `request.session` (used as storage key) and notification text fields, the critical values stored (`windowsId` and `tabId`) come from `sender.tab` which is set by the Chrome extension API and cannot be spoofed by the attacker.

When the storage is later retrieved (in notification click handlers), it uses the browser-set `windowsId` and `tabId` values for `chrome.windows.update()`, `chrome.tabs.update()`, and `chrome.tabs.sendMessage()`. The attacker cannot control these tab/window IDs to redirect operations to arbitrary tabs.

According to the methodology, storage poisoning alone is NOT a vulnerability - the stored data must flow back to the attacker or be used in an exploitable way. Here:
1. No retrieval path to attacker (no sendResponse, postMessage back)
2. Stored values used in operations are browser-set, not attacker-controlled
3. While notification display text is attacker-controlled, this is just UI manipulation on peoplefone.com domains where the content script runs, which is not a security vulnerability per the threat model

The only attacker-controlled data that persists is the session ID (used as key) and notification text, but neither provides exploitable impact beyond displaying a notification with custom text on the peoplefone.com website.
