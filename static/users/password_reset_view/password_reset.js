import { validate_password } from "../field_validators.js";
// By default can_login will be false
// And javascript will wait from user proper
// data in fields to set can_login to true.
let can_login = false;

const form_fields = document.querySelectorAll(".field");
const submit_button = document.querySelector("input[type='submit']");

const password1_field = document.querySelector("input[name='new_password1']");
const password2_field = document.querySelector("input[name='new_password2']");


function validate_form(){
    let validatedPasswords = true;
    
    if(
        (password1_field.value.length < 8 || password2_field.value.length < 8)
        || (password1_field.value !== password2_field.value)
    ){validatedPasswords = false;}

    return validatedPasswords;
}


for(let field of form_fields){
    field.addEventListener('keyup', (event) => {
        // If form have proper values then
        // enable submit button
        can_login = validate_form();
        
        submit_button.disabled = !can_login;
    });
}
