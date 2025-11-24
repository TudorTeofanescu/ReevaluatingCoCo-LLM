# CoCo Analysis: abmdngemgajijkdcpbhfgcjmhcgecbok

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 6

---

## Sink 1-4: document_eventListener_WebGUI_sendxhr → fetch_resource_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/abmdngemgajijkdcpbhfgcjmhcgecbok/opgen_generated_files/cs_0.js
Line 511	document.addEventListener('WebGUI_sendxhr', function(e) {
Line 512	console.log("1. Action received Info :" + e.detail.strurl);
Line 515	chrome.runtime.sendMessage({snapshot: "requestSnapshot", actionUrl : domainContext + e.detail.strurl, actionValue: e.detail.value, appContext: docUrl, actionAsync: e.detail.async }, function(response) {
Line 519	chrome.runtime.sendMessage({actionUrl : domainContext + e.detail.strurl, actionValue: e.detail.value, appContext: docUrl, actionAsync: e.detail.async }, function(response) {
```

**Code:**

```javascript
// Content script - Event listener
document.addEventListener('WebGUI_sendxhr', function(e) {
    console.log("1. Action received Info :" + e.detail.strurl);

    if(e.detail.strurl.indexOf("Snapshot") > 0) {
        chrome.runtime.sendMessage({
            snapshot: "requestSnapshot",
            actionUrl : domainContext + e.detail.strurl, // ← attacker-controlled
            actionValue: e.detail.value,
            appContext: docUrl,
            actionAsync: e.detail.async
        }, function(response) {});
    } else {
        chrome.runtime.sendMessage({
            actionUrl : domainContext + e.detail.strurl, // ← attacker-controlled
            actionValue: e.detail.value,
            appContext: docUrl,
            actionAsync: e.detail.async
        }, function(response) {});
    }
});

// Background script - hardcoded localhost URLs
var rtw_ipaddress = "127.0.0.1";
var rtw_portno = 7878;
var recordWebEventsURL = "http://"+ rtw_ipaddress+":" + rtw_portno + "/moeb/service/com.ibm.rational.test.rtw.webgui.service.IWebGuiRecorderService/?action=recordWebEvents";

chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.snapshot != undefined) {
        sendWebUISnapshot(request, sendResponse, sender.tab.id);
    } else if(request.actionValue != undefined) {
        sendWebUIAction(request, sendResponse, sender.tab.id);
    }
    return true;
});

function sendWebUIAction(request, sendResponse, tabId) {
    var recordWebEventsParam = {
        id: '0',
        declaredClass : 'com.ibm.rational.test.lt.core.moeb.model.transfer.testscript.WebRecorderStep',
        requestType: 1,
        uniqueId: String(tabId),
        jsonString: JSON.stringify(actionValueJsonObj)
    };
    // Sends attacker data TO hardcoded backend (localhost:7878)
    postRequest(recordWebEventsURL, JSON.stringify(recordWebEventsParam), function(xhrresponse) {
        sendResponse({response : xhrresponse});
    });
}
```

**Classification:** FALSE POSITIVE

**Reason:** This is hardcoded backend infrastructure. The attacker-controlled data (e.detail.strurl, e.detail.value) is sent TO hardcoded localhost URLs (127.0.0.1:7878). Per methodology rule 3, data TO hardcoded developer backend URLs is trusted infrastructure. The extension is designed to communicate with IBM Rational WebUI Test recorder running locally on the developer's machine. Compromising the developer's local infrastructure is outside the scope of extension vulnerabilities.

---

## Sink 5-6: document_eventListener_WebGUI_sendBrowserId → fetch_resource_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/abmdngemgajijkdcpbhfgcjmhcgecbok/opgen_generated_files/cs_0.js
Line 526	document.addEventListener('WebGUI_sendBrowserId', function(e) {
Line 527	console.log("Browser Id received Info :" + e.detail.browserId);

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/abmdngemgajijkdcpbhfgcjmhcgecbok/opgen_generated_files/bg.js
Line 1201	tabsInfoJsonString = JSON.stringify(tabsInfoJsonString);
Line 1202	var hasAnyTaskforMeURLRequest = hasAnyTaskforMeURL + tabsInfoJsonString;
```

**Code:**

```javascript
// Content script - Event listener
document.addEventListener('WebGUI_sendBrowserId', function(e) {
    console.log("Browser Id received Info :" + e.detail.browserId);
    chrome.runtime.sendMessage({browserId: e.detail.browserId}, function(response) {
        console.log("Processed Browser ID request " + response.result);
    });
});

// Background script
var hasAnyTaskforMeURL = "http://"+ rtw_ipaddress+":" + rtw_portno + "/moeb/service/com.ibm.rational.test.rtw.webgui.service.IWebGuiRecorderService?action=hasAnyClientTask&client_task=";

function enableRestAPICommunicationForRecorderLaunchedBrowser(request, sendResponse, browserId) {
    var runningTabsInfoArray = [];
    runningTabsInfoArray.push({
        url_kind : "",
        browser_type : BROWSER_NAME,
        unique_id : browserId // ← attacker-controlled
    });
    var tabsInfoJsonString = {"activeTabsInfo" :runningTabsInfoArray};
    tabsInfoJsonString = JSON.stringify(tabsInfoJsonString);
    var hasAnyTaskforMeURLRequest = hasAnyTaskforMeURL + tabsInfoJsonString;
    // Sends attacker data TO hardcoded backend (localhost:7878)
    getRequest(hasAnyTaskforMeURLRequest);
    sendResponse({result: "success"});
}
```

**Classification:** FALSE POSITIVE

**Reason:** Same as above - attacker-controlled data (e.detail.browserId) is sent TO hardcoded localhost infrastructure (127.0.0.1:7878). This is trusted developer infrastructure per methodology rule 3.
