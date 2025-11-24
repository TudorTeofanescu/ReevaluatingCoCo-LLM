# CoCo Analysis: alnkbbbeaagbhcjfdlbbkmfdjapkpgji

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 4 (all same type: XMLHttpRequest_post_sink)

---

## Sink: cs_window_eventListener_message → XMLHttpRequest_post_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/alnkbbbeaagbhcjfdlbbkmfdjapkpgji/opgen_generated_files/cs_0.js
Line 469	window.addEventListener("message", function (event) {...})
Line 491	chrome.runtime.sendMessage({ cmd: 'PrintDocuments', args: { documents: event.data.documents } }
	event.data.documents

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/alnkbbbeaagbhcjfdlbbkmfdjapkpgji/opgen_generated_files/bg.js
Line 1057	ids.push(args.documents[i].id);
	args.documents[i].id
Line 978	client.send(JSON.stringify(ids));
	JSON.stringify(ids)
```

**Code:**

```javascript
// Content script (cs_0.js, Lines 469-496)
window.addEventListener("message", function (event) {
    if (event.source != window)
        return;

    if (event.data.type && (event.data.type == "CHECK_PRINT_PROCESSOR_EXTENSION")) {
        console.log("Content script received: CHECK_PRINT_PROCESSOR_EXTENSION");
        window.postMessage({ type: "CHECK_PRINT_PROCESSOR_EXTENSION_RESULT" }, "*");
    }

    if (event.data.type && (event.data.type == "CHECK_PRINT_PROCESSOR")) {
        console.log("Content script received: CHECK_PRINT_PROCESSOR");
        chrome.runtime.sendMessage({ cmd: 'CheckPrintService', args: {} },
            function (response) {
                window.postMessage({ type: "CHECK_PRINT_PROCESSOR_RESULT", connected: response.connected }, "*");
            });
    }

    if (event.data.type && (event.data.type == "DOCUMENTS_TO_PRINT")) {
        console.log("Content script received: DOCUMENTS_TO_PRINT");
        chrome.runtime.sendMessage({ cmd: 'PrintDocuments', args: { documents: event.data.documents } },  // ← attacker-controlled
            function (response) {
                console.info('Content script received response PrintDocuments');
            });
    }
}, false);

// Background script (bg.js, Lines 963-1068)
// PrintService definition
function PrintService() {
    this.baseUrl = "http://localhost:35363/api/PrintService/";  // ← hardcoded localhost backend
    this.connected = false;
}

PrintService.prototype = {
    sendDocuments: function (ids) {
        console.log('PrintService.sendDocuments');

        var client = new XMLHttpRequest();
        client.onreadystatechange = handler;
        client.open("POST", this.baseUrl + 'send');  // ← POST to localhost:35363
        client.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        client.send(JSON.stringify(ids));  // ← attacker-controlled ids sent here

        function handler() {
            if (client.readyState === 4) {
                if (client.status === 200) {
                    console.log('PrintService.sendDocuments success');
                } else {
                    console.log('PrintService.sendDocuments fail');
                }
            }
        }
    },
    check: function (callback) {
        console.log('PrintService.check');
        var self = this;

        var client = new XMLHttpRequest();
        client.onreadystatechange = handler;
        client.open("GET", this.baseUrl + 'check');
        client.send();

        if (callback) { callback(this.connected); }

        function handler() {
            if (client.readyState === 4) {
                if (client.status === 200) {
                    self.connected = true;
                } else {
                    self.connected = false;
                }
            }
        }
    }
};

// Message handler
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.cmd === 'PrintDocuments') {
        printDocuments(request.args);
    }
    // ...
});

function printDocuments(args) {
    console.log('extension handle PrintDocuments');
    var ids = [];
    for (var i = 0, l = args.documents.length; i < l; ++i) {
        ids.push(args.documents[i].id);  // ← extract id from attacker-controlled documents
    }
    printService.sendDocuments(ids);  // ← send to localhost backend
    sendResponse({});
}
```

**Classification:** FALSE POSITIVE

**Reason:** This is a hardcoded backend URL vulnerability (False Positive Pattern X). According to the methodology Rule #3: "Hardcoded backend URLs are still trusted infrastructure - Data TO/FROM developer's own backend servers = FALSE POSITIVE."

While the flow exists and an attacker can control the data sent via window.postMessage:

1. **External attacker trigger available**: Content script runs on specific domains (manifest.json lines 12: `"*://docsbox.s7.ru/*"`, `"*://docgeneration.s7.ru/*"`, etc.), and webpage can send postMessage with type "DOCUMENTS_TO_PRINT"

2. **Attacker-controllable data**: `event.data.documents` flows through the extension to `printService.sendDocuments(ids)`

3. **BUT: Data goes to hardcoded localhost backend**: The XMLHttpRequest POST goes to `http://localhost:35363/api/PrintService/send` (hardcoded at Line 966)

The methodology explicitly states: "Attacker sending data to `hardcoded.com` = FALSE POSITIVE" and "Compromising developer infrastructure is separate from extension vulnerabilities."

This extension is designed to communicate with a local print service running on the user's machine at localhost:35363. While an attacker can trigger the extension to send arbitrary document IDs to this local service, this represents a design choice to trust the local print service infrastructure, not an extension vulnerability. The local print service is expected to validate the document IDs it receives.

**Note**: The content script only runs on specific trusted domains (s7.ru subdomains), which suggests this is an internal enterprise extension designed to work with S7 Airlines' document management system and their local print processor.
