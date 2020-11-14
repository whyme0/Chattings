let submitPrivacySettingsFormButton = document.getElementById("submitPrivacySettingsFormButton");
let privacySettingsHandlerUrl = document.currentScript.getAttribute('privacySettingsHandlerUrl');
let privacySettingsFormFields = document.querySelectorAll("#privacySettingsForm input");


let successMessageSpan = document.querySelector(".success-message");


submitPrivacySettingsFormButton.addEventListener("click", function(event){
    let formtData = getPrivacySettingFormData();
    makeAjaxRequestForPrivacySettingsForm(formtData);
});


function getPrivacySettingFormData(){
    setPrivacySettingsCheckboxValues();
    let formData = new FormData();
    for(let field of privacySettingsFormFields){
        formData.append(field.name, field.value);
    }
    return formData;
}


function setPrivacySettingsCheckboxValues(){
    let fields = document.querySelectorAll("input[type='checkbox']");

    for(let field of fields){
        field.value = field.checked;
    }
}


function makeAjaxRequestForPrivacySettingsForm(formData){
    let ajaxRequest = new XMLHttpRequest();
    
    ajaxRequest.onreadystatechange = function(){
        if(ajaxRequest.readyState == XMLHttpRequest.DONE){
            if(ajaxRequest.status == 200){
                successMessageSpan.style.display = 'inline';
            }
            else{
                console.error(ajaxRequest.response);
            }
        }
    };
    ajaxRequest.open("post", privacySettingsHandlerUrl, true);
    ajaxRequest.send(formData);
    console.log("Отправлено");

}
