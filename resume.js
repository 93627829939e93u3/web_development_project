function generateResume() {
    // Get user input values
    const name = document.getElementById("name").value;
    const contact = document.getElementById("contact").value;
    const address = document.getElementById("address").value;
    const email = document.getElementById("email").value;
    const website = document.getElementById("website").value;
    const expertise = document.getElementById("expertise").value;
    const languages = document.getElementById("languages").value;
    const interests = document.getElementById("interests").value;
    const profile = document.getElementById("profile").value;
    const education = document.getElementById("education").value;
    const experience = document.getElementById("experience").value;
    const projects = document.getElementById("projects").value;
    const photo = document.getElementById("photo").files[0];

    // Set values in the resume section
    document.getElementById("displayName").innerText = name;
    document.getElementById("displayContact").innerText = contact;
    document.getElementById("displayAddress").innerText = address;
    document.getElementById("displayEmail").innerText = email;
    document.getElementById("displayWebsite").innerText = website;
    
    const items = expertise.split(',').map(item => item.trim());
    const list = document.getElementById('dynamicList');
    items.forEach(item => {
        if (item) { // Ensure it's not empty
            const listItem = document.createElement('li');
            listItem.textContent = item;
            list.appendChild(listItem);
        }
    });
    document.getElementById('dynamicList').value = '';
    const items2 = languages.split(',').map(item => item.trim());
    const list2 = document.getElementById('dynamicList2');
    items2.forEach(item => {
        if (item) { // Ensure it's not empty
            const listItem = document.createElement('li');
            listItem.textContent = item;
            list2.appendChild(listItem);
        }
    });
    document.getElementById('dynamicList2').value = '';
    const items3 = interests.split(',').map(item => item.trim());
    const list3 = document.getElementById('dynamicList3');
    items3.forEach(item => {
        if (item) { // Ensure it's not empty
            const listItem = document.createElement('li');
            listItem.textContent = item;
            list3.appendChild(listItem);
        }
    });
    document.getElementById('dynamicList3').value = '';
    
    
    document.getElementById("displayProfile").innerText = profile;
    document.getElementById("displayEducation").innerText = education;
    document.getElementById("displayExperience").innerText = experience;
    const items4 = projects.split(',').map(item => item.trim());
    const list4 = document.getElementById('dynamicList4');
    items4.forEach(item => {
        if (item) { // Ensure it's not empty
            const listItem = document.createElement('li');
            listItem.textContent = item;
            list4.appendChild(listItem);
        }
    });
    document.getElementById('dynamicList4').value = '';

    if (photo) {
        const reader = new FileReader();
        reader.onload = function (e) {
            document.getElementById("profilePhoto").src = e.target.result;
        };
        reader.readAsDataURL(photo);
    }

    // Show the resume section and hide the form
    document.getElementById("resumeSection").style.display = "block";
    document.querySelector(".form-container").style.display = "none";
}

function editResume() {
    // Show the form and hide the resume section
    document.getElementById("resumeSection").style.display = "none";
    document.querySelector(".form-container").style.display = "block";
}

function downloadResume() {
    // Use html2pdf to download the resume
    const element = document.getElementById("resumeSection");
    html2pdf().from(element).save('resume.pdf');
}
