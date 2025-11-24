# CoCo Analysis: oncckmaelaecccmaniihojgeopkcajfh

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 32 (multiple detections of chrome_browsingData_remove_sink)

---

## Sink: Internal Extension Logic → chrome_browsingData_remove_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/oncckmaelaecccmaniihojgeopkcajfh/opgen_generated_files/bg.js
Line 1144: `chrome.browsingData.remove({"since": timeframe}, opt, proc_handlecallback);`

**Code:**

```javascript
// Background script - Message listener (bg.js Line 1084-1137)
chrome.extension.onRequest.addListener(
    function(request, sender, sendResponse) {
        switch (request.type) {
            case 'start':
                var b={};
                if (manifest && manifest.version){
                    if (manifest.version < request.minversion){
                        b.resultcode=4;
                        chrome.tabs.sendMessage(sender.tab.id, {action: "start_response", response: b});
                        break;
                    }
                }
                if (chrome.browsingData) {
                    var a=proc_clean(request.timeframe, request.opt);  // Calls cleanup function

                    if (a) b.resultcode=0;
                    else b.resultcode=1;
                } else {
                    b.resultcode=3;
                }
                chrome.tabs.sendMessage(sender.tab.id, {action: "start_response", response: b});
                break;
            // ... other cases
        }
    }
);

// Cleanup function (bg.js Line 1139-1148)
function proc_clean(timeframe,opt){
    try{
        if ((timeframe==null) || (opt==null)) return;

        if (timeframe !== undefined) {
            chrome.browsingData.remove({"since": timeframe}, opt, proc_handlecallback);
            return true;
        }
    }catch(err){}
}

// Content script check (cs_0.js Line 468-506)
// Messages only from webpage via window.postMessage
window.addEventListener("message",function(event){
    var a=event.data;
    if(!a.type) return;
    if(a.type=="btn_start"){
        proc_start(a.timeframe,a.opt,a.minversion);
    }
},false);

function proc_start(timeframe,opt,minversion){
    chrome.extension.sendRequest({type:'start', timeframe:timeframe, opt:opt, minversion:minversion});
    // ...
}
```

**Classification:** FALSE POSITIVE

**Reason:** No external attacker trigger. The content script only runs on "atomurl.net/cleaner/*" and "atomurl.net/cleanerapps/*" (developer's own domain per manifest). The window.postMessage listener receives data from the same atomurl.net webpage, which is the developer's trusted infrastructure. This is the extension's legitimate functionality - a browser cleaner tool that removes browsing data when users visit the developer's website and click the cleanup button. The developer controls both the extension and the triggering website.
