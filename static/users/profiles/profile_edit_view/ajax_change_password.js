let submitChangePasswordFormButton = document.querySelector("input[name='changePasswordBtn']");
let changePasswordHandlerUrl = document.currentScript.getAttribute('changePasswordHandlerUrl');
let changePasswordFormFields = document.querySelectorAll("#changePasswordForm input");


submitChangePasswordFormButton.addEventListener("click", function(event){
    let formData = getChangePasswordFormData();
    makeAjaxRequestForChangePasswordForm(formData);
});


function getChangePasswordFormData(){
    let formData = new FormData();
    for(let field of changePasswordFormFields){
        formData.append(field.name, field.value);
    }
    return formData;
}


function makeAjaxRequestForChangePasswordForm(formData){
    let ajaxRequest = new XMLHttpRequest();
    
    ajaxRequest.onreadystatechange = function(){
        if(ajaxRequest.readyState == XMLHttpRequest.DONE){
            if(ajaxRequest.status != 200){
                location.reload();
                return false;
            }
            else{
                console.error(ajaxRequest.response);
            }
        }
    };
    
    ajaxRequest.open("post", changePasswordHandlerUrl, true);
    ajaxRequest.send(formData);
    console.log("Отправлено");
}
