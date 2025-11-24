# CoCo Analysis: bmobkojilggkdhfginkfilecnbnkngha

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 8 (all variants of same flow)

---

## Sink: XMLHttpRequest_responseText_source → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bmobkojilggkdhfginkfilecnbnkngha/opgen_generated_files/bg.js
Line 332 XMLHttpRequest.prototype.responseText (CoCo framework mock)
Line 1023 response = JSON.parse(response)
Line 1024-1027 response.emote.name / response.code extraction
Line 1062 emotes[name] = id
Line 1063 chrome.storage.sync.set({[key]: emotes})

**Code:**

```javascript
// Background script - Hardcoded API URLs (bg.js lines 1020-1032)
let fetch = i==0 ? "https://api.frankerfacez.com/v1/emote/" : "https://api.betterttv.net/3/emotes/";
fetch += emoteID;
httpGetAsync(fetch, (response)=>{  // Fetch from hardcoded API
    response = JSON.parse(response);
    if(response.hasOwnProperty("emote") && response.emote.hasOwnProperty("name")){
        emoteName = response.emote.name;  // Extract emote name from response
    }else if(response.hasOwnProperty("code")){
        emoteName = response.code;
    }
    if(emoteName != null){
        SetStorage(key, emoteName, emoteID);  // Store in chrome.storage.sync
    }
})

// Storage function (bg.js lines 1056-1069)
function SetStorage(key, name, id){
    GetStorage(key, (res)=>{
        if(!res.hasOwnProperty(key)){res[key] = {}}
        let emotes = res[key];
        if(Object.keys(emotes).indexOf(name) < 0){
            emotes[name] = id;
            chrome.storage.sync.set({  // Storage sink
                [key]: emotes
            })
        }
    })
}

// XMLHttpRequest wrapper (bg.js lines 1076+)
function httpGetAsync(URL, callback)
{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() {
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
            callback(xmlHttp.responseText);
    }
    xmlHttp.open("GET", URL, true);
    xmlHttp.send(null);
}
```

**Classification:** FALSE POSITIVE

**Reason:** This is a hardcoded backend URL (trusted infrastructure) pattern. The extension only fetches emote metadata from two trusted third-party APIs (api.frankerfacez.com and api.betterttv.net) and stores the emote names/IDs in chrome.storage.sync. The URLs are hardcoded and not attacker-controllable. Per the methodology, "Data FROM hardcoded backend: fetch('https://api.myextension.com') → response → storage.set" is a FALSE POSITIVE because compromising the third-party API infrastructure is a separate issue from extension vulnerabilities. No external attacker can control the data flow from these hardcoded APIs to storage.
