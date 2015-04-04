/*
  HPG - The Hash Password Generator
*/

var passLength = 12;
var alphaChars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
var symbolChars = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~';

function isGoodChar(c, charset) {
    return (charset.indexOf(c) != -1);
}

function generatePassword(identifier, salt, charset, length){
    // TODO Add lookup into local storage for salt, or prompt user
    var saltHash = CryptoJS.algo.SHA512.create().finalize(salt);
    var hasher = CryptoJS.algo.SHA512.create().update(saltHash);
    var pwHash = hasher.finalize(identifier);
    var pwHashString = pwHash.toString(CryptoJS.enc.Latin1);

    var password = "";
    var i = 0;
    while(password.length < length && i < pwHashString.length) {
        var c = pwHashString.charAt(i);
        if(isGoodChar(c, charset)){
            password = password + c;
        }
        i = (i+1) % pwHashString.length;
    }
    return password;
}

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
