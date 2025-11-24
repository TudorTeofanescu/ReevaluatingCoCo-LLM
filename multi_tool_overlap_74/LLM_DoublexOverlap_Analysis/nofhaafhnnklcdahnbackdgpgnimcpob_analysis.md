# CoCo Analysis: nofhaafhnnklcdahnbackdgpgnimcpob

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** Multiple (all cookies_source → externalNativePortpostMessage_sink)

---

## Sink: cookies_source → externalNativePortpostMessage_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nofhaafhnnklcdahnbackdgpgnimcpob/opgen_generated_files/bg.js
Line 689: name: 'cookie_name'
Line 695: value: 'cookie_value'
Line 1352: cookiestr += (cookiestr ? "; " : "") + cookie.name + "=" + cookie.value;

**Code:**

```javascript
// Background script - Content script connection handler
chrome.runtime.onConnect.addListener(function(contentport) {
  var contentportid = contentport.sender.tab.id;
  contentports[contentportid] = contentport;

  // Listens for messages from content script
  contentport.onMessage.addListener(function(data, sender) {
    if (data && data.type === "com.fabasoft.nm.back.connect") {
      contentport.postMessage({ type: "com.fabasoft.nm.back.connect" });
      return;
    }

    try {
      var newport = false;
      if (!connected) {
        if (data.method == "Init") {
          replied = false;
        }
        port = connect(); // Connects to native host
        newport = true;
      }

      data.srcid = contentportid.toString();

      // Only for specific methods: Init and UpdateLoginToken
      if (data.method == "Init") {
        data.alltabids = [];
        for (var id in contentports) {
          data.alltabids.push(id.toString());
        }
        postMessageWithCookies(data, contentport, contentportid);
      }
      else if (data.method == "UpdateLoginToken") {
        postMessageWithCookies(data, contentport, contentportid);
      }
      else {
        port.postMessage(data);
      }
    } catch (e) {
      // error handling
    }
  });
});

function postMessageWithCookies(data, contentport, contentportid) {
  chrome.cookies.getAllCookieStores(function(stores) {
    var storeid = null;
    for (var i = 0; i < stores.length; i++) {
      for (var j = 0; j < stores[i].tabIds.length; j++) {
        if (stores[i].tabIds[j] === contentportid) {
          storeid = stores[i].id;
          break;
        }
      }
    }

    chrome.cookies.getAll({url:data.srcurl, storeId:storeid}, function(cookies) {
      var cookiestr = "";
      if (cookies) {
        for (var i = 0; i < cookies.length; i++) {
          var cookie = cookies[i];
          cookiestr += (cookiestr ? "; " : "") + cookie.name + "=" + cookie.value;
        }
      }
      data.indata.cookies = cookiestr;

      // Sends to native messaging host
      port.postMessage(data);
    });
  });
}

function connect() {
  var port = chrome.runtime.connectNative("com.fabasoft.nmhostpm19");
  connected = true;
  return port;
}
```

**Classification:** FALSE POSITIVE

**Reason:** The vulnerability requires internal extension trigger, not external attacker control. The flow is:
1. Content script must initiate connection via `chrome.runtime.connect()`
2. Content script must send message with `data.method == "Init"` or `"UpdateLoginToken"`
3. Cookies are then forwarded to the native messaging host

While the content script runs on `<all_urls>`, webpages cannot directly trigger or control the content script's behavior to initiate this connection and send the required messages. This is internal extension logic only, not externally triggerable by an attacker on a malicious webpage.
