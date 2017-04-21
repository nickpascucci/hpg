/**
 * UI functions for HPG's Javascript implementation.
 */

"use strict";

function getValue(name) {
    return document.getElementById(name).value;
}

function onGenerateClicked() {
    var identifier = getValue("identifier-input");
    var salt = getValue("salt-input");
    var length = getValue("length-input");
    var useSymbols = document.getElementById("symbol-input").checked;
    var charset = useSymbols ? alphaChars + symbolChars : alphaChars;
    document.getElementById("generated-input").value =
        generatePassword(identifier, salt, charset, length);
}

window.onload = function () {
    document.getElementById("generate-button").onclick = onGenerateClicked;
}
