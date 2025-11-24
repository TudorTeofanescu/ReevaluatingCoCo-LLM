# CoCo Analysis: apgphfamplbbabmclbgpebdkclodnlpl

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 18 (12 chrome_storage_sync_set_sink + 12 bg_localStorage_setItem_value_sink + 6 sendResponseExternal_sink, but many are duplicates)

---

## Sink 1-12: XMLHttpRequest_responseText_source → chrome_storage_sync_set_sink
## Sink 13-24: XMLHttpRequest_responseText_source → bg_localStorage_setItem_value_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/apgphfamplbbabmclbgpebdkclodnlpl/opgen_generated_files/bg.js
Line 332	XMLHttpRequest.prototype.responseText = 'sensitive_responseText';
Line 1154	    xmlDoc = parser.parseFromString(txt, 'text/xml');
Line 1161	    return xmlDoc.getElementsByTagName(nodeName)[0].childNodes[0].nodeValue;

**Code:**

```javascript
// Hardcoded backend URLs (Line 970-972)
g_login_url = 'https://service.prsstobe.com/ext_login_stats.php',
g_install_url = 'https://service.prsstobe.com/ext_install_stats.php',
g_install_url_fs = 'https://service.prsstobe.com/ext_install_stats.php',

// SendData makes XMLHttpRequest to hardcoded backend (Line 1168-1180)
function SendData(url, data, callback){
  var http = new XMLHttpRequest();
  http.open('POST', url, true);  // url is hardcoded backend
  http.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
  if(callback != undefined)
    http.onreadystatechange = function(){
        if(http.readyState == 4)
          if(http.status == 200)
            callback(http.responseText);  // Response from hardcoded backend
      }
  http.send(data);
}

// SendInstallStats calls SendStats with hardcoded URL (Line 1328-1339)
function SendInstallStats(callback){
  initParams(function(){
    var install_url = getInstallUrl();  // Returns g_install_url (hardcoded)

    SendStats('ext_install_stats_request', install_url,
      function(){
        ParseInstallResponse.apply(this, arguments);  // Parses response
        callback.apply(this, arguments);
      });
  })
}

// ParseInstallResponse stores backend response (Line 1199-1208)
function ParseInstallResponse(response){
  var firstTimeInstall = null;
  if(response != undefined){
    firstTimeInstall = parseXMLNode(response, 'first_install_time');
    if(firstTimeInstall != ''){
      params.set(params.FIRST_TIME_INSTALL, firstTimeInstall);  // Stores to storage
      params.set(params.DATE_OF_INSTALL, firstTimeInstall);
    }
  }
}

// params.set stores to both chrome.storage.sync and localStorage (Line 1010-1015)
set: function(name, value){
  var obj = {};
  obj[this.STORAGE_PREFIX + name] = value;
  browser_api.storage.sync.set(obj);  // Data from hardcoded backend
  localStorage.setItem(this.STORAGE_PREFIX + name, value);  // Data from hardcoded backend
}
```

**Classification:** FALSE POSITIVE

**Reason:** Data flows from hardcoded developer backend URLs (`https://service.prsstobe.com/ext_install_stats.php` and `https://service.prsstobe.com/ext_login_stats.php`) to chrome.storage.sync.set and localStorage.setItem. Per the methodology, data FROM hardcoded backend URLs represents trusted infrastructure. The developer controls the backend servers, so this is not an attacker-controllable data flow. Compromising the developer's infrastructure is a separate concern from extension vulnerabilities.

---

## Sink 25-30: cookies_source → sendResponseExternal_sink

**CoCo Trace:**
No line numbers provided in the trace. Only detection notices without code references.

**Code:**

Examining the actual extension code shows `onMessageExternal` (Line 1373-1382) only sends back simple boolean responses:
```javascript
function onMessageExternal(msg, sender, sendResponse){
  var message = msg.message != undefined ? msg.message : msg;
  if ( message == "EXTINSTALLED" && sendResponse != undefined){
    if (msg['extId'] == undefined){
      sendResponse({result: true});  // No cookie data
    }else{
      sendResponse({result: msg['extId'] == chrome.runtime.id});  // No cookie data
    }
  }
}
```

No flow from cookies to sendResponseExternal exists in the actual extension code.

**Classification:** FALSE POSITIVE

**Reason:** CoCo detected the sink but provided no line numbers or trace information showing actual code flow. The extension's `onMessageExternal` handler does not access or send any cookie data - it only sends back simple boolean result objects. This appears to be a framework-only detection with no real flow in the extension code.
