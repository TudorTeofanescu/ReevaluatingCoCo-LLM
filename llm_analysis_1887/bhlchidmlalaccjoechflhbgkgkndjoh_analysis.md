# CoCo Analysis: bhlchidmlalaccjoechflhbgkgkndjoh

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 9 (multiple detections of similar flows)

---

## Sink: cs_window_eventListener_message → XMLHttpRequest_post_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bhlchidmlalaccjoechflhbgkgkndjoh/opgen_generated_files/cs_0.js
Line 562: `window.addEventListener("message", function(event) {`
Line 567: `if (event.data.type && (event.data.type == "YG_INFO_REQ")) {`
Line 569: `chrome.runtime.sendMessage(JSON.parse(event.data.text), function(response) {`

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bhlchidmlalaccjoechflhbgkgkndjoh/opgen_generated_files/bg.js
Line 1002: `var keys = request.data;`
Line 1005: `var word = keys[key];`
Line 1060: `load_personal_dict(request.data.user);`
Line 1287: `var params = 'secret=' + Math.floor(Date.now() / 1000) + '&userid=' + user + '&date=' + '1970-01-01';`

**Code:**

```javascript
// contentscript.js (Content Script) - Lines 562-583
window.addEventListener("message", function(event) {
  if (event.source != window)
    return;

  if (event.data.type && (event.data.type == "YG_INFO_REQ")) {
    chrome.runtime.sendMessage(JSON.parse(event.data.text), function(response) {
        if (response != undefined && response.length > 0) {
            window.postMessage({ type: "YG_INFO_RESP", data: response }, "*");
        }
    });
  }
}, false);

// eventpage.js (Background) - Lines 999-1029
chrome.runtime.onMessage.addListener(function(request,sender, sendResponse) {
    if (request.type == "keys") {
        var response = Array();
        var keys = request.data; // ← attacker-controlled
        for (key in keys) {
            var word = keys[key]; // ← attacker-controlled
            var idx = ygDict.findIndex(x => x.SeekBy == word.toLowerCase());
            // ... dictionary lookup logic
            response.push(ygDict[idx]);
        }
        sendResponse(response);
    }
    else if (request.type == "load_my_dict") {
        load_personal_dict(request.data.user); // ← attacker-controlled user param
    }
});

// Lines 1284-1302
function load_personal_dict(user) {
    var url = 'https://campus.geva.co.il/ajax/vocab/getStudentWords.php';
    var params = 'secret=' + Math.floor(Date.now() / 1000) + '&userid=' + user + '&date=' + '1970-01-01';
    // ← attacker-controlled user concatenated into params
    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.responseType = 'json';
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");

    xhr.onload = function() {
        if (xhr.status === 200) {
            save_personal_dict(xhr.response);
        }
    };
    xhr.send(params); // ← params with attacker data sent to hardcoded backend
}
```

**Classification:** FALSE POSITIVE

**Reason:** Although attacker-controlled data from `event.data.text` flows through the extension and is sent via XMLHttpRequest, the destination URL is hardcoded to the developer's backend infrastructure (`https://campus.geva.co.il/ajax/vocab/getStudentWords.php`). According to the analysis methodology, sending attacker data TO hardcoded backend URLs is a FALSE POSITIVE because compromising developer infrastructure is separate from extension vulnerabilities. The developer trusts their own backend to handle any input, including potentially malicious user IDs.

**Note:** All 9 detections represent the same pattern - attacker-controlled data from postMessage being sent to the hardcoded backend URL `https://campus.geva.co.il/`, just through slightly different code paths (request.data, request.data.user, keys[key], etc.).
