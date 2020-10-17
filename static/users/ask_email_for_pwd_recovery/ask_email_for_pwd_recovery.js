import { validate_email } from "../field_validators.js";
// By default can_login will be false
// And javascript will wait from user proper
// data in fields to set can_login to true.
let can_login = false;

const form_fields = document.querySelectorAll(".field");
const submit_button = document.querySelector("input[type='submit']");

const email_field = document.querySelector("input[name='email']");


function validate_form(){
    let validatedEmail = false;

    validatedEmail = validate_email(email_field);
    return validatedEmail;
}


for(let field of form_fields){
    field.addEventListener("keyup", (event) => {
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
