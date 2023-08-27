// CSS Script

const blob = document.getElementById("blob");

window.onpointermove = event => {
    const { clientX, clientY } = event;

    blob.animate({
        left: `${clientX}px`,
        top: `${clientY}px`
    }, { duration: 3000, fill: "forwards" });
}

// File Script

var file;
var chooseBtn = document.querySelector(".choose-btn");
var fileNameDisplay = document.querySelector(".file-name-text");

chooseBtn.addEventListener("click", ()=>{
    document.querySelector("#image-ip").click();
})

document.querySelector("#image-ip").addEventListener("change", (e)=>{
    file = e.target.files[0];
    console.log(file.name);
    fileNameDisplay.innerHTML = "Selected File: " + file.name;
    checkFile();
});

function checkFile(){
    let fileType = file.type;
    let validExtensions = ["image/jpeg", "image/jpg", "image/png"];
    if(validExtensions.includes(fileType)){
        chooseBtn.innerText = "Choose Another File";
        fileReader.readAsDataURL(file);
    }
    else{
        alert("This is not an Image File!");
    }
}

function predictClick(){
    if (fileNameDisplay.innerHTML === "No File Chosen"){
        alert("No File Chosen");
        return false;
    }
}