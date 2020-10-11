import { validate_email, validate_username } from "../field_validators.js";
// By default can_login will be false
// And javascript will wait from user proper
// data in fields to set can_login to true.
let can_login = false;

const form_fields = document.querySelectorAll(".field");
const submit_button = document.querySelector("input[type='submit']");

const username_field = document.querySelector("input[name='username']");
const email_field = document.querySelector("input[name='email']");
const password1_field = document.querySelector("input[name='password1']");
const password2_field = document.querySelector("input[name='password2']");


function validate_form(){
    let validatedPasswords = true;
    let validatedUsername = validate_username(username_field);
    let validatedEmail = validate_email(email_field);

    if(
        (password1_field.value.length < 8 || password2_field.value.length < 8)
        || (password1_field.value !== password2_field.value)
    ){validatedPasswords = false;}

    return validatedPasswords && validatedUsername && validatedEmail;
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