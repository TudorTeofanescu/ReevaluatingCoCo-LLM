# CoCo Analysis: bdiahcebghgckgbgmjhdbecjkedpcidn

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_tabs_executeScript_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bdiahcebghgckgbgmjhdbecjkedpcidn/opgen_generated_files/bg.js
Line 965 - chrome.runtime.onMessageExternal.addListener receives e.testId
Line 965 - e.testId flows to _executeScript via _getInjectScriptUrlTag

**Code:**

```javascript
// Background script - External message listener
chrome.runtime.onMessageExternal.addListener(function(e,t,n){
  var r=e.url,a=e.testId,i=e.useNewEditor,o=e.config,c=e.action,d=e.useSecureApiToken;
  switch(c){
    case"launchEmbedEditor":
      TEST.url=r,TEST.testId=a,TEST.useNewEditor=i,
      // ... later calls _executeScript
  }
});

function _executeScript(e,t,n){
  // e = tab id, t = hardcoded script URL, n = testId from message
  chrome.tabs.executeScript(e,{
    code:_getInjectScriptUrlTag(t,{
      id:"abtasty-editor",
      "data-campaignid":n // testId used as attribute value only
    })
  });
}

function _getInjectScriptUrlTag(e){
  var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},
      n=LOCAL?"local.":"",
      r=Object.entries(t).reduce(function(e,t){
        var n=_slicedToArray(t,2),r=n[0],a=n[1];
        return e+'\nscript.setAttribute("'+r+'", "'+a+'");'
      },""),
      a="\n        var script = document.createElement('script');\n        script.src = '"+n+e+"';\n        "+r+"\n        (document.head || document.documentElement).appendChild(script);\n    ";
  return a
}

// Hardcoded script URL being injected
var o="https://teddytor.abtasty.com/dist/main.js";
_executeScript(e,o,TEST.testId);
```

**Classification:** FALSE POSITIVE

**Reason:** While external messages can trigger code execution via `chrome.tabs.executeScript`, the actual script being injected has a hardcoded URL (`https://teddytor.abtasty.com/dist/main.js`). The external `testId` parameter is only used as an HTML attribute value (`data-campaignid`), not as executable code. The extension is also limited by `externally_connectable` to only `*.abtasty.com/*` domains. No attacker-controlled code execution occurs.
