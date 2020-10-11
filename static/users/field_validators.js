function validate_username(fieldObj=null, fieldName=null){
    /**
     Validate username field in form

     @param {Node} fieldObj Node object.
     @param {String} fieldName Name of username field.
    */
    let usernameField = fieldObj || document.querySelector(`input[type=${fieldName}]`);
    let usernameRegex = /^[\w-]+$/gm;

    return usernameRegex.test(usernameField.value);
}


function validate_email(fieldObj=null, fieldName=null){
    /**
     Validate email field in form

     @param {Node} fieldObj Node object.
     @param {String} fieldName Name of email field.
    */

    let emailField = fieldObj || document.querySelector(`input[type=${fieldName}]`);

    if(
        (emailField.value.length < 5)
        || (emailField.value.indexOf('@') == -1)
        || (emailField.value.indexOf('.') == -1)
    ){return false;}
    else{return true}
}


function validate_password(fieldObj=null, fieldName=null){
    /**
     Validate password field in form

     @param {Node} fieldObj Node object.
     @param {String} fieldName Name of password field.
    */

   let passwordField = fieldObj || document.querySelector(`input[type=${fieldName}]`);

   if(
       (passwordField.value.length < 8)
   ){return false;}
   else{return true;}
}

export {validate_email, validate_username, validate_password};