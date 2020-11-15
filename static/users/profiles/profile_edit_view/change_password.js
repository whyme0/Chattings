import {validate_password} from "../../field_validators.js";

let isFormValid = false;

const oldPasswordField = document.getElementById("id_old_password");
const newPassword1Field = document.getElementById("id_new_password1");
const newPassword2Field = document.getElementById("id_new_password2");

const submitButton = document.querySelector("input[name='changePasswordBtn']");

const formFields = document.querySelectorAll(".field");


function validate_form(){
    let isOldPasswordValidated = validate_password(oldPasswordField);
    
    if(
        isOldPasswordValidated
        & (newPassword1Field.value.length >= 8)
        & (newPassword2Field.value.length >= 8)
        & (newPassword1Field.value == newPassword2Field.value)
    ){
        return true;
    }
    
    return false;
}


for(let field of formFields){
    field.addEventListener('keyup', (event) => {
        // If form have proper values then
        // enable submit button

        submitButton.disabled = !validate_form();
    });
}
