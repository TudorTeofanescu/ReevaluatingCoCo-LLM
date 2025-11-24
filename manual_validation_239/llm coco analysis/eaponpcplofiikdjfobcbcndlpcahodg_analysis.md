# CoCo Analysis: eaponpcplofiikdjfobcbcndlpcahodg

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/eaponpcplofiikdjfobcbcndlpcahodg/opgen_generated_files/bg.js
Line 965: `e.subId`

**Code:**

```javascript
// Background script (background.min.js)
chrome.runtime.onMessageExternal.addListener(function(e,t,n){
    e.subId?(
        console.log("Received subId from webpage - ",e.subId),
        setStorage("validsubid",e.subId) // ← attacker-controlled subId stored
    ):console.log("Error receiving message from website",e)
})

function setStorage(e,t){
    chrome.storage.local.set({[e]:t}).then(()=>{ // Storage sink
        console.log("Value is set for key:",e)
    })
}

// Later usage of validsubid:
function isPaidUser(e){
    chrome.storage.local.get(["validsubid"],function(t){
        testPaid?e(!0):e(!!t.validsubid)
    })
}

function checkSubscriptionStatus(){
    chrome.storage.local.get(["validsubid"],e=>{
        let t=e.validsubid;
        t&&fetch(domain+"subscription/"+t+"/valid") // → to hardcoded backend
            .then(e=>{
                if(200===e.status)return e.json();
                throw Error(`HTTP status ${e.status}`)
            })
            .then(e=>{
                e.valid||chrome.storage.local.remove("validsubid",()=>{
                    console.log("Subscription is invalid, removed validsubid.")
                })
            })
    })
}
```

**Classification:** FALSE POSITIVE

**Reason:** While external messages from whitelisted domains (thealtx.com) can write arbitrary data to storage via `chrome.runtime.onMessageExternal`, this is incomplete storage exploitation. The stored `validsubid` value is only used to make requests to the developer's hardcoded backend (`https://app.thealtx.com/subscription/${validsubid}/valid`), not sent back to the attacker. There is no retrieval path where the attacker can observe or receive the stored data. Storage poisoning alone without attacker-accessible output is not exploitable.
