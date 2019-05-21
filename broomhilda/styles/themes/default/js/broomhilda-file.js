function initFile(inputElement, options) {
    if (typeof inputElement == "string") {
        document.querySelectorAll(inputElement).forEach(function(tabs) { initFile(tabs, options); });

        return;
    }

    if (inputElement.hasOwnProperty('each')) {
        inputElement.each(function(tabs) { initFile(tabs, options); });

        return;
    }

    if (inputElement.hasOwnProperty('forEach')) {
        inputElement.forEach(function(tabs) { initFile(tabs, options); });

        return;
    }

    parentElement = inputElement.parentNode;
    labelElement = parentElement.querySelector("label.file-upload")

    var context = {
        settings: {},
        inputElement: inputElement,
        labelElement: labelElement
    };

    inputElement.addEventListener(
        "change",
        (function() {
            var text = "";

            for (var i = 0; i < this.inputElement.files.length; i++) {
                text += this.inputElement.files[i].name;
                // TODO: display size and type
            }

            this.labelElement.innerText = text;
        }).bind(context));
}
