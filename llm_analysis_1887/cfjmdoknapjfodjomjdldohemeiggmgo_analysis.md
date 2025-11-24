# CoCo Analysis: cfjmdoknapjfodjomjdldohemeiggmgo

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cfjmdoknapjfodjomjdldohemeiggmgo/opgen_generated_files/bg.js
Line 965: Multiple references to the flow
- `e.data`
- `e.data.access_token`
- `e.data.access_token.replace("Bearer ","")`

**Code:**

```javascript
// Background script (bg.js line 965) - External message handler
chrome.runtime.onMessageExternal.addListener(((e,t,o)=>{
    if(e.data){
        if(e.data.access_token){
            let t=e.data.access_token.replace("Bearer ",""); // ← attacker-controlled
            chrome.storage.local.set({access_token:t},(function(){
                chrome.storage.local.set({isLoggedIn:!0},(function(){}))
            }))
        }
        if(e.data.hasLoggedOut&&!0===e.data.hasLoggedOut){
            chrome.storage.local.set({access_token:""},(function(){
                chrome.storage.local.set({isLoggedIn:!1},(function(){}))
            }))
        }
    }
}));

// Background script - Internal message handler showing storage usage
chrome.runtime.onMessage.addListener(((e,t,o)=>{
    if(e.loadListNames>0&&void 0!==typeof e.loadListNames){
        let t,a=e.loadListNames;
        return chrome.storage.local.get(["access_token"],(e=>{
            t=e.access_token; // Retrieved stored token
            const s=new Headers({"Content-Type":"application/json",Authorization:`Bearer ${t}`}),
            n=`https://api.nameshouts.com/api/v2.0/user/user-list?user_list_id=${a}`; // Hardcoded backend
            fetch(n,{method:"GET",headers:s}) // Fetch to hardcoded backend
                .then((e=>e.json()))
                .then((e=>{o(e)}))
                .catch((e=>{console.error(e)}))
        })),!0
    }
    // Similar patterns for loadLangs and nameToSearch...
}));
```

**Classification:** FALSE POSITIVE

**Reason:** This is a FALSE POSITIVE due to hardcoded backend URLs (trusted infrastructure). The flow shows storage poisoning where an attacker from app2.nameshouts.com (whitelisted in externally_connectable) can set an arbitrary access_token. However, the stored token is only used for Authorization headers in fetch requests to the hardcoded backend api.nameshouts.com. The attacker can poison the token, but it only affects communication with the developer's own trusted backend (api.nameshouts.com). This is analogous to sending attacker data to a hardcoded backend, which the methodology explicitly classifies as FALSE POSITIVE. The developer trusts their own infrastructure; compromising api.nameshouts.com would be an infrastructure issue, not an extension vulnerability.
