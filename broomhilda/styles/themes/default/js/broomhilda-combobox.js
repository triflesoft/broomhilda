function initComboBox(controlElement, options) {
    if (typeof controlElement == "string") {
        document.querySelectorAll(controlElement).forEach(function(combobox) { initComboBox(combobox, options); });

        return;
    }

    if (controlElement.hasOwnProperty('each')) {
        controlElement.each(function(combobox) { initComboBox(combobox, options); });

        return;
    }

    if (controlElement.hasOwnProperty('forEach')) {
        controlElement.forEach(function(combobox) { initComboBox(combobox, options); });

        return;
    }

    function defaultSearch(query, controlElement) {
        result = []

        controlElement.querySelectorAll("option").forEach(
            function(element) {
                if (element.innerText.toLowerCase().indexOf(query.toLowerCase()) >= 0) {
                    result.push({ "value": element.value, "text": element.innerText });
                }
            });

        return result;
    }

    function defaultSelect(value, controlElement) {
        option = null

        controlElement.querySelectorAll("option").forEach(
            function(element) {
                if (element.value == value) {
                    option = element;
                }
            });

        if (option) {
            return {"value": value, "text": option.innerText};
        }

        return null;
    }

    function defaultRenderText(dataItem) {
        return dataItem.text;
    }

    function defaultRenderHtml(dataItem, searchQuery) {
        var leftIndex = dataItem.text.toLowerCase().indexOf(searchQuery.toLowerCase());

        if (leftIndex == -1) {
            return dataItem.text;
        }

        var rightIndex = leftIndex + searchQuery.length;

        return dataItem.text.substring(0, leftIndex) +
            "<mark>" +
            dataItem.text.substring(leftIndex, rightIndex) +
            "</mark>" +
            dataItem.text.substring(rightIndex, dataItem.text.length);
    }

    function updateSelection(context) {
        if (context.selectedItem == null) {
            context.searchQuery = "";
            context.inputElement.value = "";
            context.controlElement.value = "";
        } else {
            context.searchQuery = context.settings.renderText(context.selectedItem);
            context.inputElement.value = context.searchQuery;
            context.controlElement.value = context.selectedItem.value;
        }
    }

    function isEnabled(controlElement) {
        if (controlElement.disabled || controlElement.readOnly) {
            return false;
        }

        return true;
    }

    function showDropdown(context) {
        var fontSizeText = window.getComputedStyle(document.querySelector("body")).getPropertyValue("font-size");
        var fontSize = Number(fontSizeText.substring(0, fontSizeText.length - 2));

        if (!context.isDropdownOpen) {
            var parentNode = context.controlElement.parentNode;

            while ((!parentNode.classList.contains("field")) && (parentNode.tagName != "BODY")) {
                parentNode = parentNode.parentNode;
            }

            if (!parentNode) {
                console.error("comboBox must be child of \".field\".");
                return;
            }

            context.isDropdownOpen = true;

            if (parentNode.classList.contains("error")) {
                context.dropdownElement.classList.add("error");
            } else {
                context.dropdownElement.classList.remove("error");
            }

            parentNode.scrollIntoView({ block: "start", inline: "nearest" });

            var inputRect = context.inputElement.getBoundingClientRect();
            var inputTop  = 0;
            var inputLeft = 0;
            var offsetElement = context.inputElement;

            while (offsetElement != null) {
                inputTop += offsetElement.offsetTop;
                inputLeft += offsetElement.offsetLeft;
                offsetElement = offsetElement.offsetParent;
            }

            context.inputElement.select();
            context.dropdownElement.style.left    = Math.round(inputLeft - fontSize) + "px";
            context.dropdownElement.style.top     = Math.round(inputTop + inputRect.height - 0.16 * fontSize) + "px";
            context.dropdownElement.style.width   = Math.round(inputRect.width             + 2.00 * fontSize) + "px";
            context.dropdownElement.style.zIndex  = 9999;
            context.dropdownElement.style.display = "block";

            updateSearchResult(context, true);

            return true;
        }

        return false;
    }

    function hideDropdown(context) {
        context.dropdownElement.style.display = "none";

        if (context.isDropdownOpen) {
            context.isDropdownOpen = false;

            updateSelection(context);

            return true;
        }

        return false;
    }

    function updateSearchResult(context, force) {
        searchQuery = context.inputElement.value;

        if ((context.searchQuery != searchQuery) || force) {
            context.items = context.settings.search(searchQuery, context.controlElement);

            if (context.selectedItem == null) {
                if (context.items.length > 0) {
                    context.selectedItem = context.items[0];
                }
            }

            ulElement = context.dropdownElement.querySelector("ul.combobox-list");
            ulElement.innerHTML = "";

            context.items.forEach(function(item, index) {
                liElement = document.createElement("li");
                liElement.innerHTML = context.settings.renderHtml(item, searchQuery);
                liElement.setAttribute("data-value", item.value);
                liElement.setAttribute("data-index", index);

                if (item.value == context.selectedItem.value) {
                    liElement.classList.add("selected");
                }

                liElement.addEventListener("mousedown", function(event){
                    var dataValue = event.target.getAttribute("data-value");
                    var selectedItem = null;

                    context.items.forEach(function(i) {
                        if (i.value == dataValue) {
                            selectedItem = i;
                        }
                    });

                    setSelectedItem(context, selectedItem);
                });

                ulElement.appendChild(liElement);
            });

            if (context.isDropdownOpen && (context.items.length > 0)) {
                setSelectedItem(context, context.items[0]);
            } else {
                setSelectedItem(context, null);
            }

            context.searchQuery = searchQuery;
        }
    }

    function setSelectedItem(context, item) {
        liElement = context.dropdownElement.querySelector("li.selected");

        if (liElement) {
            liElement.classList.remove("selected");
        }

        if (item) {
            liElement = context.dropdownElement.querySelector("li[data-value=\"" + item.value + "\"]");

            if (liElement) {
                var liRect = liElement.getBoundingClientRect();
                var liTop  = liElement.offsetTop;
                var dropdownRect = context.dropdownElement.getBoundingClientRect();
                var dropdownTop  = context.dropdownElement.offsetTop;

                if (
                    (liTop < dropdownTop) ||
                    (liTop + liRect.height > dropdownRect.height)) {
                    liElement.scrollIntoView({ block: "center" });
                }

                liElement.classList.add("selected");
                context.selectedItem = item;
            } else {
                context.selectedItem = null;
            }
        }
        else {
            context.selectedItem = null;
        }
    }

    function selectFirstItem(context) {
        if (context.isDropdownOpen && (context.items.length > 0)) {
            setSelectedItem(context, context.items[0]);

            return true;
        }

        return false;
    };

    function selectLastItem(context) {
        if (context.isDropdownOpen && (context.items.length > 0)) {
            setSelectedItem(context, context.items[context.items.length - 1]);

            return true;
        }

        return false;
    };

    function selectNextItem(context) {
        if (context.isDropdownOpen && (context.items.length > 0)) {
            liSelected = context.dropdownElement.querySelector("li.selected");

            if (liSelected) {
                var index = Number(liSelected.getAttribute("data-index"));

                index = (index + 1) % context.items.length;

                setSelectedItem(context, context.items[index]);
            } else {
                setSelectedItem(context, context.items[0]);
            }

            return true;
        }

        return false;
    };

    function selectPrevItem(context) {
        if (context.isDropdownOpen && (context.items.length > 0)) {
            liSelected = context.dropdownElement.querySelector("li.selected");

            if (liSelected) {
                var index = Number(liSelected.getAttribute("data-index"));

                index = (index + context.items.length - 1) % context.items.length;

                setSelectedItem(context, context.items[index]);
            } else {
                setSelectedItem(context, context.items[0]);
            }

            return true;
        }

        return false;
    };

    var searchFunction = options && options.hasOwnProperty('search') ? options.search : defaultSearch;
    var selectFunction = options && options.hasOwnProperty('select') ? options.select : defaultSelect;
    var renderTextFunction = options && options.hasOwnProperty('renderText') ? options.renderText : defaultRenderText;
    var renderHtmlFunction = options && options.hasOwnProperty('renderHtml') ? options.renderHtml : defaultRenderHtml;
    var dropdownElement = document.createElement('div');

    dropdownElement.innerHTML = "<div><ul class=\"combobox-list\"></ul></div>";
    dropdownElement.classList.add("combobox-dropdown");
    dropdownElement.style.display = "none";

    controlElement.parentNode.insertBefore(dropdownElement, null);

    var inputElement = document.createElement('input');

    inputElement.classList.add("combobox-input");
    inputElement.setAttribute("type", "text");
    inputElement.setAttribute("autocomplete", "off");
    inputElement.setAttribute("autocapitalize", "off");

    var context = {
        settings: {
            search: searchFunction,
            select: selectFunction,
            renderText: renderTextFunction,
            renderHtml: renderHtmlFunction,
        },
        controlElement: controlElement,
        inputElement: inputElement,
        dropdownElement: dropdownElement,
        isDropdownOpen: false,
        items: [],
        searchQuery: "",
        selectedItem: null,
    };

    inputElement.addEventListener(
        "focus",
        (function() {
            if (!isEnabled(context.controlElement)) {
                return;
            }

            showDropdown(this);
        }).bind(context));
    inputElement.addEventListener(
        "click",
        (function() {
            if (!isEnabled(context.controlElement)) {
                return;
            }

            showDropdown(this);
        }).bind(context));
    inputElement.addEventListener(
        "blur",
        (function() {
            hideDropdown(this);
        }).bind(context));
    inputElement.addEventListener(
        "keyup",
        (function() {
            if (!isEnabled(context.controlElement)) {
                return;
            }

            updateSearchResult(this, false);
        }).bind(context));
    inputElement.addEventListener(
        "keydown",
        (function(event)
        {
            if (!isEnabled(context.controlElement)) {
                if ((event.keyCode != 9) && (event.keyCode != 13)) {
                    event.preventDefault();
                }

                return;
            }

            switch(event.keyCode) {
                //case   8: // backspace
                //    break;
                //case   9: // tab
                //    break;
                case  13: // enter
                case 108: // numpad enter
                    if (hideDropdown(this)) {
                        event.preventDefault();
                    }
                    break;
                case  27: // escape
                    if (hideDropdown(this)) {
                        event.preventDefault();
                    }
                    break;
                case  33: // page up
                case  38: // up
                    if (selectPrevItem(this)) {
                        event.preventDefault();
                    }
                    break;
                case  34: // page down
                case  40: // down
                    if (selectNextItem(this)) {
                        event.preventDefault();
                    }
                    break;
                case  35: // end
                    if (selectLastItem(this)) {
                        event.preventDefault();
                    }
                    break;
                case  36: // home
                    if (selectFirstItem(this)) {
                        event.preventDefault();
                    }
                    break;
                default:
                    showDropdown(this);
                    break;
            }
        }).bind(context));

    controlElement.style.display = "none";
    controlElement.parentNode.insertBefore(inputElement, controlElement);
    window.addEventListener("resize", (function() { hideDropdown(this); }).bind(context) );

    var selectedValue = null;

    if (controlElement.nodeName == "INPUT") {
        inputElement.readOnly = controlElement.disabled || controlElement.readOnly;
        selectedValue = controlElement.value;
    } else if (controlElement.nodeName == "SELECT") {
        inputElement.readOnly = controlElement.disabled;
        selectedOption = controlElement.querySelector("option[selected]");

        if (selectedOption) {
            selectedValue = selectedOption.value;
        }
    }

    if (selectedValue) {
        context.selectedItem = context.settings.select(selectedValue, controlElement);
        updateSelection(context);
    }
}
