# CoCo Analysis: fbpooiglbphclofdkobibfooddmehifa

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 18 (multiple duplicate detections of 3 unique flows)

---

## Sink 1: document_eventListener_loadGradeKeys → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/fbpooiglbphclofdkobibfooddmehifa/opgen_generated_files/cs_0.js
Line 476	document.addEventListener("loadGradeKeys", function(data){
	data
Line 477	  chrome.runtime.sendMessage(data.detail);
	data.detail

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/fbpooiglbphclofdkobibfooddmehifa/opgen_generated_files/bg.js
Line 1012	        if(request.type == "info"){
	request.type

**Code:**

```javascript
// Content script - cs_0.js Line 476-477
document.addEventListener("loadGradeKeys", function(data){
  chrome.runtime.sendMessage(data.detail); // ← attacker-controlled via DOM event
});

// Background script - bg.js Line 1010-1025
chrome.runtime.onMessage.addListener(
  function(request, sender, sendResponse) {
    if(request.type == "info"){
      chrome.storage.local.set({"testData": request},function(){ setBadge() })
    } else if(request.type == "config"){
      chrome.storage.local.set({"settings": request},function(){
        console.log("saved settings");
        console.log(request);
      })
    } else {
      chrome.storage.local.set({"scores": request},function(){
        console.log("saved score data");
        console.log(request);
      })
    }
  }
)
```

**Classification:** FALSE POSITIVE

**Reason:** This is incomplete storage exploitation. The flow shows attacker data → storage.set only, without any retrieval path. Per the methodology: "Storage poisoning alone (storage.set without retrieval) is NOT exploitable. The attacker MUST be able to retrieve the poisoned data back (via sendResponse, postMessage, or triggering a read operation that sends data to attacker-controlled destination)." There is no evidence in the code that the stored data flows back to the attacker or is used in any exploitable operation. The data is only stored and used internally by the extension.

---

## Sink 2: document_eventListener_loadTestData → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/fbpooiglbphclofdkobibfooddmehifa/opgen_generated_files/cs_0.js
Line 480	document.addEventListener("loadTestData", function(data){
	data
Line 481	  chrome.runtime.sendMessage(data.detail);
	data.detail

**Code:**

```javascript
// Content script - cs_0.js Line 480-481
document.addEventListener("loadTestData", function(data){
  chrome.runtime.sendMessage(data.detail); // ← attacker-controlled via DOM event
});

// Same background handler as Sink 1
```

**Classification:** FALSE POSITIVE

**Reason:** Same as Sink 1 - incomplete storage exploitation. Attacker can poison storage but cannot retrieve the data. No exploitable impact.

---

## Sink 3: document_eventListener_loadPasteSettings → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/fbpooiglbphclofdkobibfooddmehifa/opgen_generated_files/cs_0.js
Line 484	document.addEventListener("loadPasteSettings", function(data){
	data
Line 485	  chrome.runtime.sendMessage(data.detail);
	data.detail

**Code:**

```javascript
// Content script - cs_0.js Line 484-485
document.addEventListener("loadPasteSettings", function(data){
  chrome.runtime.sendMessage(data.detail); // ← attacker-controlled via DOM event
});

// Same background handler as Sink 1
```

**Classification:** FALSE POSITIVE

**Reason:** Same as Sink 1 - incomplete storage exploitation. Attacker can poison storage but cannot retrieve the data. No exploitable impact.

---
