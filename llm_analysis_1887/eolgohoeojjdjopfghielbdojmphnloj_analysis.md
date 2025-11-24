# CoCo Analysis: eolgohoeojjdjopfghielbdojmphnloj

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 4 (2 to chrome_storage_sync_set_sink, 2 to jQuery_ajax_settings_data_sink)

---

## Sink 1: XMLHttpRequest_responseText_source → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/eolgohoeojjdjopfghielbdojmphnloj/opgen_generated_files/bg.js
Line 332: XMLHttpRequest.prototype.responseText = 'sensitive_responseText';
Line 993: var parseResult = JSON.parse(xhr.responseText);
Line 995: var email = parseResult["email"];

**Code:**

```javascript
// Background script (bg.js) - Line 981
function fetchEmail() {
  chrome.identity.getAuthToken({ interactive: true }, function(token) {
    if (chrome.runtime.lastError) {
      console.log(chrome.runtime.lastError);
      return;
    }

    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
      if( xhr.readyState == 4 ) {
        if( xhr.status == 200 ) {
          var parseResult = JSON.parse(xhr.responseText); // Response from Google API
          var email = parseResult["email"]; // Extract email

          chrome.storage.sync.set({"account_id": email}, function() { // Store email
            sendPushToApp({ // Send to hardcoded Parse API
              "where": {
                "account_id": email
              },
              "data": {
                "action":"com.marketlytics.idlenotifier.LINKED_CHROME",
                "completed": true
              }
            });
          });
        }
      }
    };

    xhr.open("GET","https://www.googleapis.com/oauth2/v1/userinfo",true); // Hardcoded Google API
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('Authorization', "OAuth " + token );
    xhr.send(null);
  });
}
```

**Classification:** FALSE POSITIVE

**Reason:** The flow involves data FROM a hardcoded backend URL (`https://www.googleapis.com/oauth2/v1/userinfo` - Google's OAuth API). This is trusted infrastructure. The extension fetches the user's email from Google's legitimate API using OAuth token, stores it, then sends it to another hardcoded backend (`https://api.parse.com/1/push`). Attackers cannot control the response from Google's API without compromising Google's infrastructure, which is outside the scope of extension vulnerabilities.

---

## Sink 2: XMLHttpRequest_responseText_source → jQuery_ajax_settings_data_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/eolgohoeojjdjopfghielbdojmphnloj/opgen_generated_files/bg.js
Line 332: XMLHttpRequest.prototype.responseText = 'sensitive_responseText';
Line 993: var parseResult = JSON.parse(xhr.responseText);
Line 995: var email = parseResult["email"];
Line 977: data: JSON.stringify(data)

**Code:**

```javascript
// Background script (bg.js) - Line 968
function sendPushToApp(data) {
  $.ajax({
    type : 'POST',
    url: 'https://api.parse.com/1/push', // Hardcoded Parse API backend
    beforeSend: function(request) {
      request.setRequestHeader("X-Parse-Application-Id", 'Af5csnypaP7pFMfcstzbynrZIAP9nKKzFH9kMTri');
      request.setRequestHeader("X-Parse-REST-API-Key", '0CMWzWog3kLcit6FI6R6bYcC5M1hG9PynXZjJ7fo');
      request.setRequestHeader("Content-Type", 'application/json');
    },
    data: JSON.stringify(data) // Data includes email from Google API
  });
}

// Called from fetchEmail() after getting email from Google
chrome.storage.sync.set({"account_id": email}, function() {
  sendPushToApp({
    "where": {
      "account_id": email // Email from Google OAuth
    },
    "data": {
      "action":"com.marketlytics.idlenotifier.LINKED_CHROME",
      "completed": true
    }
  });
});
```

**Classification:** FALSE POSITIVE

**Reason:** This flow is data FROM hardcoded Google API TO hardcoded Parse API backend. Both are trusted infrastructure. The flow is: Google OAuth API → email → storage.sync.set → Parse API push notification. The destination URL is hardcoded (`https://api.parse.com/1/push`), and the data originates from Google's legitimate OAuth API. Attackers cannot control either the source (Google) or the destination (Parse) without compromising those services, which is an infrastructure issue, not an extension vulnerability.

---

## Sink 3 & 4: Duplicate detections

The remaining two sinks (lines 79-109 in used_time.txt) are duplicate detections of the same flows already analyzed above, just triggered at different execution paths during CoCo's analysis.
