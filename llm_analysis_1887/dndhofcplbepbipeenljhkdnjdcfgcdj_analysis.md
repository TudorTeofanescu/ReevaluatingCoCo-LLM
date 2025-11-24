# CoCo Analysis: dndhofcplbepbipeenljhkdnjdcfgcdj

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 17 (multiple flows from bg_chrome_runtime_MessageExternal to XMLHttpRequest_url_sink and XMLHttpRequest_post_sink)

---

## Sink: bg_chrome_runtime_MessageExternal → XMLHttpRequest_url_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dndhofcplbepbipeenljhkdnjdcfgcdj/opgen_generated_files/bg.js
Line 1153: `hoverCoolMapCell(request.rowNode, request.colNode);`
Line 1208: `var url = COOLMAP_MATRICES_HOVER_URL + "?row_node=" + rowNode + "&column_node=" + colNode;`

**Code:**

```javascript
// Background script - Constants (bg.js Lines 1084-1087)
var COOLMAP_URL = "http://localhost:10725/coolmap/";
var COOLMAP_MATRIX_URL = COOLMAP_URL + "matrices/";
var COOLMAP_PROPERTY_TABLE_URL = COOLMAP_URL + "propertyTables/";
var COOLMAP_MATRICES_HOVER_URL = COOLMAP_MATRIX_URL + "hover/";
var IGV_URL = "http://127.0.0.1:60151";

// External message handler (bg.js Lines 1149-1168)
chrome.runtime.onMessageExternal.addListener(
    function (request, sender, sendResponse) {
        if (!coolMapTalkEnabled) return false;
        if (request.type === "hoverCoolMapCell") {
            hoverCoolMapCell(request.rowNode, request.colNode); // ← attacker-controlled params
        } else if (request.type === "selectCoolMapNodes") {
            selectCoolMapNodes(request.matrixId, request.nodes); // ← attacker-controlled params
        } else if (request.type === "importCoolMapPropertyTable") {
            importCoolMapPropertyTable(request.propertyTableId, sendResponse); // ← attacker-controlled params
        } else if (request.type === "searchIGVGenes") {
            searchIGVGenes(request.genes); // ← attacker-controlled params
        }
        return true;
    }
);

// Function that constructs URLs (bg.js Lines 1202-1213)
function hoverCoolMapCell(rowNode, colNode) {
    if (rowNode === null || colNode === null) {
        return;
    }
    var xmlhttp = new XMLHttpRequest();
    var url = COOLMAP_MATRICES_HOVER_URL + "?row_node=" + rowNode + "&column_node=" + colNode;
    // ← attacker-controlled rowNode and colNode in query params
    xmlhttp.open("GET", url, true);
    xmlhttp.send();
}

// Similar patterns in other functions:
// Line 1172: var url = COOLMAP_PROPERTY_TABLE_URL.concat(propertyTableID);
// Line 1188: var url = COOLMAP_MATRIX_URL.concat(matrixID);
// Line 1208: var url = COOLMAP_MATRICES_HOVER_URL + "?row_node=" + rowNode + "&column_node=" + colNode;
// Line 1252: var url = COOLMAP_MATRIX_URL.concat(selectedMatrixId, "/selections?data_scope=displayed");
// Line 1413: var url = IGV_URL.concat("/goto?locus=", genes.join(" "));
```

**Classification:** FALSE POSITIVE

**Reason:** All XMLHttpRequest flows go to hardcoded localhost URLs that are part of the extension's intended architecture. The extension is designed to communicate with local applications (CoolMap, Cytoscape, IGV) running on `http://localhost:10725/` and `http://127.0.0.1:60151`.

According to the methodology, this falls under "Hardcoded Backend URLs (Trusted Infrastructure)." The extension description explicitly states: "This extension talks to local applications such as CoolMap, Cytoscape, and IGV when using AHub." The localhost URLs represent the developer's trusted local application infrastructure.

While external websites (whitelisted in `externally_connectable`) can send messages with attacker-controlled parameters, those parameters are only used to construct requests to localhost applications that the user has intentionally installed and is running. The attacker cannot:
- Control the base URL (hardcoded to localhost)
- Achieve cross-origin attacks (requests stay on localhost)
- Execute arbitrary code or download files
- Exfiltrate data to attacker-controlled servers

The parameters only affect which local API endpoints are called, which is the intended functionality of a local application integration extension. No exploitable impact exists beyond the intended behavior of communicating with user's local trusted applications.
