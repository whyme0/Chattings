import { validate_username, validate_password, validate_email } from "../field_validators.js";
// By default can_login will be false
// And javascript will wait from user proper
// data in fields to set can_login to true.
let can_login = false;

const form_fields = document.querySelectorAll(".field");
const submit_button = document.querySelector("input[type='submit']");

const username_field = document.querySelector("input[name='username']");
const password_field = document.querySelector("input[name='password']");


function validate_form(){
    let validatedUsername = false;
    let validatedPassword = false;
    
    if(username_field.value.indexOf('@') == -1){
        validatedUsername = validate_username(username_field);
    } else{
        validatedUsername = validate_email(username_field);
    }
    validatedPassword = validate_password(password_field);

    return validatedUsername && validatedPassword;
}


for(let field of form_fields){
    field.addEventListener('keyup', (event) => {
        // If form have proper values then
        // enable submit button
        if (validate_form()){
            can_login = true;
        }
        else{
            can_login = false;
        }
        
        submit_button.disabled = !can_login;
    });
}
