# CoCo Analysis: mbljojmeanmcfpmpelgipeacbaijjeof

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: cs_window_eventListener_wf_tagIconMapId → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mbljojmeanmcfpmpelgipeacbaijjeof/opgen_generated_files/cs_0.js
Line 508: window.addEventListener("wf_tagIconMapId", function(evt) {
Line 509: tagIconMapId = evt.detail;

**Code:**

```javascript
// cs_0.js - Content script on workflowy.com
window.addEventListener("wf_tagIconMapId", function(evt) {
  tagIconMapId = evt.detail; // Attacker-controlled via CustomEvent
  chrome.storage.sync.set({tagIconMapId:tagIconMapId}); // Storage write
  buildTagIconMap(tagIconMapId); // Uses the attacker-controlled ID
  console.log('building tag icon map from received map id from WF');
}, false);

function buildTagIconMap(id){
  const code = `
  var mapNodeId = '${id}'; // ID injected into script
  var mapNode = WF.getItemById(mapNodeId);
  var children = mapNode.getVisibleChildren();
  var map = [];
  children.forEach(function(item) {
    var icon = item.getNoteInPlainText();
    var tag = WF.getItemNameTags(item)[0];
    if (tag) {
      tag = tag['tag'];
    };
    map.push({'tag':tag, 'icon':icon})
  });

  var event = new CustomEvent("wf_tagIconMap", {detail: map});
  window.dispatchEvent(event);
  `;
  var s = document.createElement('script');
  s.textContent = code; // Injects script with attacker-controlled ID
  s.onload = function() {
    this.remove();
  };
  (document.head || document.documentElement).appendChild(s);
};

// Storage retrieval (no exfiltration path)
chrome.storage.sync.get({'tagIconMapId':'None'}, function(result) {
  if (result.tagIconMapId != 'None') {
    var tagIconMapId = result.tagIconMapId;
    buildTagIconMap(tagIconMapId); // Used locally only
  }
});
```

**Classification:** FALSE POSITIVE

**Reason:** While an attacker on workflowy.com can dispatch CustomEvent to poison storage with a malicious ID, this is **incomplete storage exploitation**. The stored value is retrieved and used locally in `buildTagIconMap()`, but there is no path for the attacker to retrieve the poisoned data back (no sendResponse, postMessage, or fetch to attacker-controlled URL). Storage poisoning alone without a retrieval mechanism is not exploitable per the methodology. The ID is also used in `buildTagIconMap()` where it's injected into a script template, but this script only runs in the same webpage context that the attacker already controls, so it doesn't elevate privileges or provide additional attack surface beyond what the attacker already has by controlling the webpage.

---

## Sink 2: cs_window_eventListener_wf_tagIconMap → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mbljojmeanmcfpmpelgipeacbaijjeof/opgen_generated_files/cs_0.js
Line 540: window.addEventListener("wf_tagIconMap", function(evt) {
Line 541: tagIconMap = evt.detail;

**Code:**

```javascript
// cs_0.js - Content script on workflowy.com
window.addEventListener("wf_tagIconMap", function(evt) {
  tagIconMap = evt.detail; // Attacker-controlled map data
  chrome.storage.sync.set({stored_tag_icon_map:tagIconMap}); // Storage write
  buildStyles(); // Uses attacker data to build CSS
}, false);

function buildStyles(){
  var styleString = '';
  tagIconMap.forEach(function(item) {
    var tag = item.tag; // Attacker-controlled
    var icon = item.icon; // Attacker-controlled
    element = document.body;
    var tagStyles = window.getComputedStyle(element);
    var fontSize = tagStyles.getPropertyValue('font-size');
    const styleTagHide = `
    span.contentTag[title="Filter ${tag}"] {
        margin-left:12px;
        font-size:0;
        line-height:0;
    }
    span.contentTag[title="Filter ${tag}"]::after{
        font-size:${fontSize};
        content:"${icon}"; // Attacker-controlled icon injected
        margin-left:-12px;
    }
    `;
    styleString = styleString.concat(styleTagHide);
  });
  style = document.getElementById('vwf_style');
  style.textContent = styleString; // CSS injection in same page context
};

// Storage retrieval (no exfiltration path)
function getRootMap(){
  chrome.storage.sync.get(['stored_tag_icon_map'], function(result) {
    tagIconMap = result.stored_tag_icon_map; // Retrieved locally only
  })
  return tagIconMap;
};
```

**Classification:** FALSE POSITIVE

**Reason:** While an attacker on workflowy.com can dispatch CustomEvent to poison storage with malicious tag/icon data, this is **incomplete storage exploitation**. The stored map is retrieved via `getRootMap()` but only used locally to build CSS styles in the same webpage context. There is no path for the attacker to retrieve the poisoned data back (no sendResponse, postMessage, or fetch to attacker-controlled URL). The CSS injection occurs in the same page context that the attacker already controls, providing no privilege escalation. Storage poisoning without a retrieval mechanism back to the attacker is not exploitable per the methodology.
