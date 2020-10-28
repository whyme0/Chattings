let profileInfoOpenButton = document.getElementById("profileInfoOpenButton");
let profileChannelsOpenButton = document.getElementById("profileChannelsOpenButton");

let dropdownProfileInfo = document.querySelector(".dropdown__profile-info");
let dropdownProfileChannels = document.querySelector(".dropdown__profile-channels");

profileInfoOpenButton.onclick = function(){
    if (dropdownProfileInfo.style.display === "none"){
        profileInfoOpenButton.innerText = "Close profile info";
        dropdownProfileInfo.style.display = "block";
    }
    else {
        profileInfoOpenButton.innerText = "Show profile info";
        dropdownProfileInfo.style.display = "none";
    }
}


profileChannelsOpenButton.onclick = function(){
    if (dropdownProfileChannels.style.display === "none"){
        profileChannelsOpenButton.innerText = "Close profile channels";
        dropdownProfileChannels.style.display = "block";
    }
    else {
        profileChannelsOpenButton.innerText = "Show profile channels";
        dropdownProfileChannels.style.display = "none";
    }
}