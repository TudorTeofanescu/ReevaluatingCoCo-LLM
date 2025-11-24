# CoCo Analysis: hiejidhjgjpelfgldfhmnaoahnephhfg

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** Multiple (cookies_source → externalNativePortpostMessage_sink)

---

## Sink: cookies_source → externalNativePortpostMessage_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hiejidhjgjpelfgldfhmnaoahnephhfg/opgen_generated_files/bg.js
Line 689     name: 'cookie_name',
Line 695     value: 'cookie_value'
Line 1352    cookiestr += (cookiestr ? "; " : "") + cookie.name + "=" + cookie.value;
```

**Code:**

```javascript
// Background script - Content script connection handler (bg.js Line 1152)
chrome.runtime.onConnect.addListener(function(contentport) {
  var contentportid = contentport.sender.tab.id;
  contentports[contentportid] = contentport;

  contentport.onMessage.addListener(function(data, sender) {
    // Line 1179-1254: Forward messages to native messaging host
    if (data.method == "Init") {
      postMessageWithCookies(data, contentport, contentportid);
    }
    else if (data.method == "UpdateLoginToken") {
      postMessageWithCookies(data, contentport, contentportid);
    }
  });
});

// Line 1301-1373: Attach cookies and send to native host
function postMessageWithCookies(data, contentport, contentportid)
{
  chrome.cookies.getAllCookieStores(function(stores) {
    // Find cookie store for the tab
    var storeid = null;
    for (var i = 0; i < stores.length; i++) {
      for (var j = 0; j < stores[i].tabIds.length; j++) {
        if (stores[i].tabIds[j] === contentportid) {
          storeid = stores[i].id;
          break;
        }
      }
    }
    // Get cookies and attach to message
    chrome.cookies.getAll({url:data.srcurl, storeId:storeid}, function(cookies) {
      var cookiestr = "";
      if (cookies) {
        for (var i = 0; i < cookies.length; i++) {
          var cookie = cookies[i];
          cookiestr += (cookiestr ? "; " : "") + cookie.name + "=" + cookie.value;
        }
      }
      data.indata.cookies = cookiestr;
      // Send to native messaging host
      port.postMessage(data);
    });
  });
}
```

**Classification:** FALSE POSITIVE

**Reason:** The cookie data flows to a native messaging host (nativeMessaging permission in manifest), not to an attacker-accessible output. This is the Fabasoft Folio extension communicating with its own native desktop application for legitimate enterprise document management purposes. The native messaging host is part of the extension's trusted infrastructure, installed on the user's machine and controlled by Fabasoft. Sending cookies to the native host is intended functionality for SSO/authentication purposes, not a vulnerability. There is no path for an external attacker to receive this cookie data, as it only flows to the local native application controlled by the extension developer.
