# CoCo Analysis: jgbkfdjdcbohgenpccfgldadaofnfknl

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jgbkfdjdcbohgenpccfgldadaofnfknl/opgen_generated_files/bg.js
Line 965 - chrome.runtime.onMessageExternal.addListener handler

**Code:**

```javascript
// Background script - Line 965 in bg.js
chrome.runtime.onMessageExternal.addListener((function(e,n,a){
    // ... other handlers ...
    if("addProgramNotify"===e.name) {
        chrome.storage.local.get({notifySeconds:60},(function(n){
            var o=e.programTime-1e3*n.notifySeconds,
            i=new Date(e.programTime),
            r=i.getMonth()+1+"/"+i.getDate()+" "+i.getHours()+"時"+i.getMinutes()+"分";
            t(e.programID,e.channel,e.channelName,e.programTime,o,e.programTitle,
                (function(){
                    chrome.notifications.create("add_"+e.programID,{
                        type:"basic",
                        iconUrl:"/images/add.png",
                        title:e.site+"から「"+e.programTitle+"」を通知登録しました。",
                        message:"AbemaTVの"+e.channelName+"チャンネルの番組「"+e.programTitle+"」("+r+")が通知登録されました。"
                    },(function(e){a({result:"added"})}))
                }),
                (function(e){a({result:e})})
            )
        }))
    }
    // ... other handlers ...
}))

// Function t() stores data to chrome.storage.local.set
function t(e,t,n,o,a,i,r,s){
    var c,l="progNotify_"+t+"_"+e;
    // ... permission check ...
    var m={};
    m[l]={
        channel:t,
        channelName:n,
        programID:e,
        programTitle:i,
        programTime:o,  // ← attacker-controlled
        notifyTime:a
    };
    chrome.storage.local.set(m,(function(){
        // Data stored but NOT sent back to attacker
        r()
    }))
}
```

**Classification:** FALSE POSITIVE

**Reason:** This is storage poisoning without retrieval. While external messages can write attacker-controlled data (programTime, programTitle, channel, etc.) to chrome.storage.local.set, the stored data is never retrieved and sent back to the attacker. The data is only used internally for alarm notifications. Per the methodology, "storage poisoning alone is NOT a vulnerability" - the attacker must be able to retrieve the poisoned data via sendResponse, postMessage, or other accessible output. No such retrieval path exists in this code.
