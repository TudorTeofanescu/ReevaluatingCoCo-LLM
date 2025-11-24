# CoCo Analysis: ibjbdljnechfamiabmolmojegeindnpc

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ibjbdljnechfamiabmolmojegeindnpc/opgen_generated_files/bg.js
Line 965 (minified background.js code)

**Code:**

```javascript
// Background - External message handler (background.js minified)
chrome.runtime.onMessageExternal.addListener(e(function(r,e,t){
    // ... extensive handler code for various message types ...

    if(r.device){  // Device-related messages
        c("currentDevice",r.device);

        if("deviceChanged"===r.message){
            d.heatmap.device=r.device;
            if(d&&d.currentTab&&d.VWOTabs.includes(d.currentTab.id)){
                d.tabDeviceMap[d.currentTab.id]=h(r.device);
                c("tabDeviceMap",d.tabDeviceMap);
                chrome.storage.local.get(["preventUseragentUpdate","vwoEditorHeatmapOrigin"]).then(function(e){
                    var t=e.preventUseragentUpdate,e=e.vwoEditorHeatmapOrigin;
                    return k({
                        tabId:d.currentTab.id,
                        newUserAgent:h(r.device),
                        preventUseragentUpdate:t,
                        tabSource:d.tabSourceUrlMap[d.currentTab.id],
                        vwoEditorHeatmapOrigin:e
                    })
                });
            }
            c("heatmap",d.heatmap);
        }
        // ... similar patterns for recordingDeviceChanged, editorDeviceChanged ...
    }

    else if("accountUpdated"===r.message && r.accountId){
        chrome.storage.local.set({accountId:r.accountId});  // ← SINK: Store attacker-controlled accountId
    }

    else if("App.Background.newTabEditor"===r.message){
        c("isNewTabEditorEnabled",r.status);  // ← Stores to globals which are synced to storage
    }

    else if("VWOApp.updateAccountId"===r.message && r.data.accountId){
        chrome.storage.local.set({accountId:r.data.accountId});  // ← SINK: Store attacker-controlled accountId
    }

    // ... many other message handlers ...
}));

// Function c() stores to globals object which is synced to chrome.storage.local
function c(e,t){
    d&&(d[e]=t);
    o.then(function(){
        d[e]=t;
        chrome.storage.local.set({globals:d});  // ← SINK: Stores entire globals object
    });
}
```

**Classification:** FALSE POSITIVE

**Reason:** While the extension has `chrome.runtime.onMessageExternal` that processes external messages and stores data to `chrome.storage.local`, there are critical issues:

1. **Restricted Attack Surface:** The extension has `externally_connectable` restricted to `*://*.vwo.com/*` and `*://*.vwo.me/*` in manifest.json. While the methodology says to IGNORE manifest restrictions, the actual vulnerability analysis still requires a complete exploitation chain.

2. **Incomplete Storage Exploitation:** The attacker (from vwo.com domains or, ignoring restrictions, any external source) can poison storage by sending external messages with various fields (device, accountId, status, etc.). However, there is NO retrieval path that sends the stored data back to the attacker:
   - The stored data is used internally for extension configuration (device settings, account IDs, tab mappings)
   - The data is sent to content scripts via `chrome.tabs.sendMessage`, not back to the external sender
   - There is no `sendResponse` call that returns storage data to the external message sender
   - The stored values control extension behavior but don't flow back to an attacker-accessible output

3. **No Exploitable Impact:** The stored configuration values (device type, account ID, editor settings) are used to:
   - Configure heatmap/recording functionality
   - Set user agent strings for specific tabs
   - Control extension UI behavior
   - None of these lead to code execution, privileged cross-origin requests, or data exfiltration accessible to the attacker

Per the methodology, storage poisoning alone (storage.set without retrieval path to attacker) is NOT a vulnerability. The methodology explicitly states: "Storage poisoning alone is NOT a vulnerability. For TRUE POSITIVE, stored data MUST flow back to attacker via: sendResponse / postMessage to attacker, Used in fetch() to attacker-controlled URL, Used in executeScript / eval, Any path where attacker can observe/retrieve the poisoned value."

In this case, there is no such retrieval path - the data stays within the extension's internal state and is not accessible to the attacker.

