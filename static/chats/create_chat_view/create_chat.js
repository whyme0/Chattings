let can_create_chat = false;

const createChatForm = document.getElementById("createChatForm");
const createChatButton = document.getElementById("createChatButton");

const formFields = document.querySelectorAll("input[type='text']");
const labelField = document.getElementById("id_label");
const nameField = document.getElementById("id_name");


function validateForm(){
    let validatedLabel = false;
    let validatedName = false;

    if ( 0 < labelField.value.length){
        validatedLabel = true;
    }
    if (0 < nameField.value.length){
        validatedName = true;
    }

    return validatedLabel && validatedName;
}


for(let field of formFields){
    field.addEventListener('keyup', (event) => {
        can_create_chat = validateForm();
        
        createChatButton.disabled = !can_create_chat;
    });
}
