var text = getValue("c_first_lang_of_literacy_full_input");
text = text.toLowerCase();
var list = getValue("langlist");
var matching_list = "";

if (text.trim() === "") {
    matching_list = "....."; 
} else {
    for (var i = 0; i < list.length; i++) {
        if (list[i].toLowerCase().indexOf(text) === 0) {
            matching_list += list[i].charAt(0).toUpperCase() + list[i].slice(1) + ", ";
        }
    }
}

if (matching_list.trim() !== "") {
    matching_list = matching_list.slice(0, -2);
    setValue("g1_l1_input_autocomplete", matching_list.trim());
} else {
    setValue("g1_l1_input_autocomplete", text);
}