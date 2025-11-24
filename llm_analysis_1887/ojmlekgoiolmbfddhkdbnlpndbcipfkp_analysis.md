# CoCo Analysis: ojmlekgoiolmbfddhkdbnlpndbcipfkp

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2 (duplicate detections of same flow)

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ojmlekgoiolmbfddhkdbnlpndbcipfkp/opgen_generated_files/bg.js
Line 967    if (msg.session) {
Line 972    msg.session.sessionTime = new Date().valueOf();

**Code:**

```javascript
// Background script - sessionGrabber.js
chrome.runtime.onMessageExternal.addListener(function (msg, sender, sendResponse) {
    if (msg.session) {
        console.log("Session msg: " + JSON.stringify(msg))
        chrome.storage.local.get(["session"], function (items) {
            var oldSession = items.session;

            msg.session.sessionTime = new Date().valueOf(); // ← attacker-controlled msg.session
            chrome.storage.local.set({"session": msg.session}); // ← Storage write sink
            if (!oldSession || oldSession.session != msg.session.session) {
                console.log("notification created")
                chrome.notifications.create('new-session-created-notification', {
                    type: 'basic',
                    iconUrl: 'img/logo-128.png',
                    title: 'Session Updated',
                    message: 'A new session has been created\nClick the icon to start presenting!',
                    contextMessage: msg.session.session
                }, function (notificationId) {
                });
            }
        });
    }
});

// Storage is retrieved but not sent back to attacker
chrome.runtime.onMessage.addListener(function (msg, sender, sendResponse) {
    if (msg.action == "sessionUpdate") {
        chrome.storage.local.get(["session"], function (items) {
            console.log(items)
            if (items && items.session) {
                $.extend(msg.session, items.session);
            }
            chrome.storage.local.set({"session": msg.session}, function () {
            });
            // No sendResponse with session data
        });
    }
});
```

**Classification:** FALSE POSITIVE

**Reason:** Storage poisoning alone without retrieval path. The attacker can write arbitrary data to chrome.storage.local via external messages, but there is no code path that retrieves the poisoned session data and sends it back to the attacker via sendResponse, postMessage, or any other attacker-accessible output. Per the methodology, storage poisoning without retrieval is not exploitable.
