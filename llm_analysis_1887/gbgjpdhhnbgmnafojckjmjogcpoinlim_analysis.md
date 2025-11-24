# CoCo Analysis: gbgjpdhhnbgmnafojckjmjogcpoinlim

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 3

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (request.player_id)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gbgjpdhhnbgmnafojckjmjogcpoinlim/opgen_generated_files/bg.js
Line 3427: if (request.player_id) {
Line 3430: LocalStorage.set({"playerId":request.player_id});

**Code:**

```javascript
// Background script (bg.js lines 3420-3446)
chrome.runtime.onMessageExternal.addListener(
    function(request, sender, sendResponse) {
        if (request.event == "open"){
            FV2Notification.gameTab = sender.tab.id;
            LocalStorage.set({LAST_TABID_KEY:sender.tab.id});
            StatsManager.count("xpress_open", "game", "click");

            // Sink 1: Store player_id
            if (request.player_id) {
                LocalStorage.get(["playerId"], function(data) {
                    if(!data.hasOwnProperty("playerId")) {
                        LocalStorage.set({"playerId":request.player_id}); // ← stores attacker-controlled value
                    }
                });
            }

            // Sink 2: Store notif_interval
            if (request.notif_interval) {
                LocalStorage.get(["notifInterval"], function(data) {
                    if(!data.hasOwnProperty("notifInterval")) {
                        LocalStorage.set({"notifInterval":request.notif_interval}); // ← stores attacker-controlled value
                    }
                });
            }

            // Sink 3: Store redirectToFB
            if (request.hasOwnProperty('redirectToFB')) {
                LocalStorage.set({"REDIRECT_TO_FB_KEY": request.redirectToFB}); // ← stores attacker-controlled value
            }

            sendResponse({hasLatestExtension:true});
        }
    });

// LocalStorage is a wrapper around chrome.storage.local (lines 3289-3297)
var LocalStorage = new function(){
    var self = this;
    self.get = function(keys, callback){
        chrome.storage.local.get(keys, callback);
    };
    self.set = function(items, callback){
        chrome.storage.local.set(items, callback);
    };
};
```

**Classification:** FALSE POSITIVE

**Reason:**

**Incomplete Storage Exploitation - No Retrieval Path to Attacker:**

1. **Storage Write Only:** The extension allows the external message sender (from https://*.farm2.zynga.com/* per manifest externally_connectable) to write three values to storage: playerId, notifInterval, and REDIRECT_TO_FB_KEY.

2. **No Retrieval Path:** The attacker CANNOT retrieve the stored data:
   - sendResponse only returns `{hasLatestExtension:true}` - a hardcoded value
   - No postMessage to webpage
   - No fetch/XHR to attacker-controlled URL
   - The stored data is used only internally by the extension

3. **How Stored Data is Used:**
   - **playerId & notifInterval:** Used for game notifications (sent to hardcoded Zynga backend URLs)
   - **REDIRECT_TO_FB_KEY:** Used as a boolean flag to choose between two hardcoded URLs:
     - If false: redirects to `ZDC_CANVAS_URL` (https://zyngagames.com/play/farmville-two)
     - Otherwise: redirects to `CANVAS_URL` (https://apps.facebook.com/farmville-two)
   - Both URLs are hardcoded constants (lines 1864-1865)

4. **No Arbitrary URL Control:** Even though the attacker can set REDIRECT_TO_FB_KEY, they can only choose between two hardcoded developer URLs. The code at lines 3454-3462 shows:
   ```javascript
   var redirectURL = CANVAS_URL + "?" + fbsource;  // Default
   if (data["REDIRECT_TO_FB_KEY"] == false) {
       redirectURL = ZDC_CANVAS_URL + "?" + fbsource;  // Alternative
   }
   ```
   The attacker cannot inject an arbitrary URL; they can only toggle between two trusted Zynga/Facebook URLs.

**According to the methodology:**
- **Rule 2 & Pattern Y:** "Storage poisoning alone is NOT a vulnerability. For TRUE POSITIVE, stored data MUST flow back to attacker via sendResponse/postMessage/fetch to attacker URL/executeScript/any path where attacker can observe/retrieve the poisoned value."
- The attacker can poison storage but CANNOT retrieve the values or cause any exploitable impact.

**Extension Purpose:** This is the official Farmville 2 X-Press extension by Zynga. The externally_connectable whitelist restricts messages to https://*.farm2.zynga.com/*, meaning only Zynga's official game website can send these messages. This is legitimate communication between the game and its companion extension.

---

## Sink 2: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (request.notif_interval)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gbgjpdhhnbgmnafojckjmjogcpoinlim/opgen_generated_files/bg.js
Line 3434: if (request.notif_interval) {
Line 3437: LocalStorage.set({"notifInterval":request.notif_interval});

**Classification:** FALSE POSITIVE

**Reason:** Same as Sink 1 - incomplete storage exploitation without retrieval path to attacker.

---

## Sink 3: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (request.redirectToFB)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gbgjpdhhnbgmnafojckjmjogcpoinlim/opgen_generated_files/bg.js
Line 3441: if (request.hasOwnProperty('redirectToFB')) {
Line 3442: LocalStorage.set({"REDIRECT_TO_FB_KEY": request.redirectToFB});

**Classification:** FALSE POSITIVE

**Reason:** Same as Sink 1 - incomplete storage exploitation without retrieval path to attacker. Additionally, the stored value only controls a boolean choice between two hardcoded trusted URLs, not arbitrary URL injection.
