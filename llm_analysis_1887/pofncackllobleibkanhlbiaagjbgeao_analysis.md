# CoCo Analysis: pofncackllobleibkanhlbiaagjbgeao

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** Multiple (cookies_source → sendResponseExternal_sink x6, XMLHttpRequest_responseText_source → chrome_storage_sync_set_sink + bg_localStorage_setItem_value_sink x8)

---

## Sink 1-6: cookies_source → sendResponseExternal_sink

**CoCo Trace:**
No line numbers provided in CoCo output - only internal trace IDs

**Code:**

```javascript
// Background script - Only external message handler found
function onMessageExternal(msg, sender, sendResponse){
  var message = msg.message != undefined ? msg.message : msg;
  if ( message == "EXTINSTALLED" && sendResponse != undefined){
    if (msg['extId'] == undefined){
      sendResponse({result: true}); // Only sends boolean
    }else{
      sendResponse({result: msg['extId'] == browser_api.runtime.id}); // Only sends boolean
    }
  }
}

browser_api.runtime.onMessageExternal.addListener( onMessageExternal );
```

**Classification:** FALSE POSITIVE (referenced only CoCo framework code)

**Reason:** CoCo provided no line numbers for this flow, indicating detection only in framework code. The actual extension code's onMessageExternal handler only sends back boolean values ({result: true/false}), never cookies.

---

## Sink 7-14: XMLHttpRequest_responseText_source → chrome_storage_sync_set_sink + bg_localStorage_setItem_value_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pofncackllobleibkanhlbiaagjbgeao/opgen_generated_files/bg.js
Line 332: XMLHttpRequest.prototype.responseText = 'sensitive_responseText';
Line 1265: xmlDoc = parser.parseFromString(txt, 'text/xml');
Line 1272: return xmlDoc.getElementsByTagName(nodeName)[0].childNodes[0].nodeValue;

**Code:**

```javascript
// brand.js - Hardcoded backend URLs
var g_login_url = 'https://service.prsstobe.com/ext_login_stats.php',
    g_install_url = 'https://service.prsstobe.com/ext_install_stats.php',
    g_install_url_fs = 'https://service.prsstobe.com/ext_install_stats.php';

// background.js - Send data to hardcoded backend
function SendData(url, data, callback){
  var http = new XMLHttpRequest();
  http.open('POST', url, true);
  http.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
  if(callback != undefined)
    http.onreadystatechange = function(){
        if(http.readyState == 4)
          if(http.status == 200)
            callback(http.responseText); // Response from hardcoded backend
      }
  http.send(data);
}

function SendStats(type, url, callback){
  // ... builds XML with extension stats
  SendData(url, data_with_header_content, callback); // Always to hardcoded backend
}

// Parse response from hardcoded backend
function ParseInstallResponse(response){
  if (g_encryption_key != "") response = decryptResponse(response);
  var firstTimeInstall = null;
  if(response != undefined){
    firstTimeInstall = parseXMLNode(response, 'first_install_time'); // Parse data from hardcoded backend
    if(firstTimeInstall != ''){
      params.set(params.FIRST_TIME_INSTALL, firstTimeInstall); // Store in storage
      params.set(params.DATE_OF_INSTALL, firstTimeInstall);
    }
  }
}

// Storage helper
params.set = function(name, value){
  var obj = {};
  obj[this.STORAGE_PREFIX + name] = value;
  browser_api.storage.sync.set(obj); // Store data from hardcoded backend
  localStorage.setItem(this.STORAGE_PREFIX + name, value);
}
```

**Classification:** FALSE POSITIVE

**Reason:** Data flows FROM hardcoded backend URLs (service.prsstobe.com) to storage. This is trusted infrastructure - the developer trusts their own backend. Compromising the backend is an infrastructure security issue, not an extension vulnerability. Storage poisoning alone without attacker-accessible retrieval path is not exploitable.
