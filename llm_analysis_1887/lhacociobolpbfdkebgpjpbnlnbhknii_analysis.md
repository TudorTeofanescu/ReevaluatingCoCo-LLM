# CoCo Analysis: lhacociobolpbfdkebgpjpbnlnbhknii

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1 (fetch_source → chrome_storage_local_set_sink)

---

## Sink: fetch_source → chrome_storage_local_set_sink (referenced only CoCo framework code)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lhacociobolpbfdkebgpjpbnlnbhknii/opgen_generated_files/bg.js
Line 265: responseText = 'data_from_fetch' (CoCo framework mock code)

CoCo only detected flow in framework code. The actual extension code (after third "// original" marker at line 963) shows the real flow.

**Code:**

```javascript
// Background script - OAuth flow with Salesforce (Lines 1058-1148)

// Step 1: Exchange OAuth code for token
exchangeCodeForToken = (code) => {
  fetch('https://' + loginType + '.salesforce.com/services/oauth2/token?...', { // ← hardcoded Salesforce URL
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded', accept: 'application/json' }
  }).then(response => response.json())
  .then(data => { // ← data from Salesforce OAuth
    data.hasOwnProperty('access_token') && setAccessToken(data)
  })
}

// Step 2: Get user info and store credentials
setAccessToken = (data) => {
  const org = {
    connectionInfo: data, // ← OAuth data from Salesforce
    loginTime: getCurrentTime(),
    sessionId: data.access_token,
    serverUrl: data.instance_url + "/services/Soap/u/" + apiVersion + "/" + organizationId,
    sandbox: loginType == "login" ? "false" : "true"
  }

  // Fetch user info from Salesforce
  fetch('https://' + loginType + '.salesforce.com/services/oauth2/userinfo', { // ← hardcoded Salesforce URL
    method: 'GET',
    headers: { Authorization: 'Bearer ' + org.sessionId }
  }).then(response => response.json())
  .then(data => {
    Object.assign(org, { oAuthInfo: data }); // ← merge userinfo from Salesforce

    // Fetch additional user details via SOAP API
    fetch(org.serverUrl, { // ← Salesforce SOAP endpoint
      method: 'POST',
      headers: { Authorization: 'Bearer ' + org.sessionId, SOAPAction: 'getUserInfo' },
      body: '<?xml version="1.0"...>'
    }).then(response => response.body)
    .then(data => {
      const userInfo = parseXmlToJson(data).getUserInfoResponse.result;
      setOrg({
        u: userInfo.userName,
        o: Object.assign(org, { userInfo: userInfo }), // ← all fetch data in org
        c: (orgs) => { chrome.runtime.sendMessage({ action: "OAUTH_SUCCEED" }) }
      })
    })
  })
}

// Line 1043-1047: setOrg stores in chrome.storage.local
setOrg = (args) => {
  getOrgs((n)=>{
    n[args.u] = args.o; // ← org object with all Salesforce fetch data
    chrome.storage.local.set({ Credentials: n }, args.c(n)) // ← stored
  })
}
```

**Classification:** FALSE POSITIVE

**Reason:** Data originates from hardcoded Salesforce OAuth2 and API URLs (https://[login|test].salesforce.com). These are trusted infrastructure - the developer's intended OAuth provider (Salesforce). The extension is designed to authenticate with Salesforce and store credentials. Compromising Salesforce infrastructure is outside the scope of extension vulnerabilities. No external attacker can control this OAuth flow or the data returned from Salesforce's official OAuth endpoints.
