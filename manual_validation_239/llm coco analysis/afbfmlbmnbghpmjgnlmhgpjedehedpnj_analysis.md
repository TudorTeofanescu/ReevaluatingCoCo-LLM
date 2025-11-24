# CoCo Analysis: afbfmlbmnbghpmjgnlmhgpjedehedpnj

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** Multiple XMLHttpRequest_url_sink detections

---

## Sink: cs_window_eventListener_mouseup → XMLHttpRequest_url_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/afbfmlbmnbghpmjgnlmhgpjedehedpnj/opgen_generated_files/cs_0.js
Line 566	function firepop_evMouseUp(ev)
Line 573	var range = document.caretRangeFromPoint(ev.clientX, ev.clientY);
Line 649	var str = range.startContainer.textContent
Line 683	return "" + offset + "," + str.substr(topIndex, lastIndex-topIndex);

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/afbfmlbmnbghpmjgnlmhgpjedehedpnj/opgen_generated_files/bg.js
Line 1155	path = "cont/1?" + param.substring(0, maxurl);
Line 1179	var url = "http://localhost:8100/v1/" + path;

**Code:**

```javascript
// Content script - cs_0.js
function firepop_evMouseUp(ev) {
    // Triggered by mouseup event
    var range = document.caretRangeFromPoint(ev.clientX, ev.clientY);
    var str = firepop_buildSearchWord(range); // Extracts text from DOM
    var url = document.location.href;

    chrome.runtime.sendMessage({msg: "popup", str: str, url: url}, function(response){
        // ...
    });
}

// Background script - bg.js
chrome.runtime.onMessage.addListener(handleMessage);

function handleMessage(request, sender, sendResponse) {
    if (request.msg == "popup") {
        firepop_popupText(request.str, request.url, sendResponse);
    }
}

function firepop_popupText(str, url, sendResponse) {
    firepop_poke("Dictionary", "PopupSearch3", str);
}

function firepop_poke(topic, item, param) {
    // ... parameter processing ...
    if (param.length > maxurl) {
        path = "cont/1?" + param.substring(0, maxurl);
    } else {
        path = topic + "/" + item + "?" + param;
    }
    firepop_puthttp(path);
}

function firepop_puthttp(path) {
    var url = "http://localhost:8100/v1/" + path; // Hardcoded localhost URL
    var xhr = new XMLHttpRequest();
    xhr.open("PUT", url, true);
    // ...
}
```

**Classification:** FALSE POSITIVE

**Reason:** The data flow exists but sends attacker-influenced data (selected text from webpage) to a hardcoded localhost backend URL (http://localhost:8100/v1/). According to the methodology, "hardcoded backend URLs are still trusted infrastructure" - sending data TO a hardcoded developer backend is a FALSE POSITIVE. The localhost server is part of the extension's trusted infrastructure (native dictionary application), not an attacker-controlled destination.
