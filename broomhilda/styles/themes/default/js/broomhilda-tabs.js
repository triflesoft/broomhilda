function initTabs(containerElement, options) {
    if (typeof containerElement == "string") {
        document.querySelectorAll(containerElement).forEach(function(tabs) { initTabs(tabs, options); });

        return;
    }

    if (containerElement.hasOwnProperty('each')) {
        containerElement.each(function(tabs) { initTabs(tabs, options); });

        return;
    }

    if (containerElement.hasOwnProperty('forEach')) {
        containerElement.forEach(function(tabs) { initTabs(tabs, options); });

        return;
    }

    function setSelectedTab(context, id) {
        context.headerElement.querySelectorAll("label").forEach(function(element) {
            element.classList.remove("selected");
        });

        context.headerElement.querySelector("label[for=" + id + "]").classList.add("selected");

        context.contentElement.querySelectorAll(".tab-content").forEach(function(element) {
            element.style.display = "none";
        });

        context.contentElement.querySelector(".tab-content[data-id=" + id + "]").style.display = "block";
    }

    headerElement = containerElement.querySelector(".header");
    contentElement = containerElement.querySelector(".content");

    var context = {
        settings: {},
        containerElement: containerElement,
        headerElement: headerElement,
        contentElement: contentElement
    };

    selectedInputElement = headerElement.querySelector("input[type=radio][checked]");

    if (!selectedInputElement) {
        selectedInputElement = headerElement.querySelector("input[type=radio]");
    }

    if (selectedInputElement) {
        selectedInputElement.checked = true;
        setSelectedTab(context, selectedInputElement.getAttribute("id"));
    }

    headerElement.querySelectorAll("input[type=radio]").forEach(
        function(element) {
            element.addEventListener("change", (function(event) {
                setSelectedTab(this, event.target.getAttribute("id"));
            }).bind(context));
        }
    );
}
