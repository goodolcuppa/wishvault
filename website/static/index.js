function deleteItem(itemId) {
    fetch('/delete-item', {
        method: "POST",
        body: JSON.stringify({ itemId: itemId})
    }).then((_res) => {
        window.location.href = "/";
    });
}

function findItem() {
    fetch('/find-item', {
        method: "POST",
        body: JSON.stringify({ url: document.getElementById("url").value })
    });
}

const ul = document.getElementById("ul-tags");
const categoryInput = document.getElementById("categories");

// initialise categories
let categories = [];
if (ul) {
    ul.querySelectorAll("li").forEach(
        li => categories.push(li.getElementsByTagName("span")[0].innerText.split(" ")[0])
    );
}
createCategory();

function createCategory() {
    ul.querySelectorAll("li").forEach(li => li.remove());
    categories.slice().reverse().forEach(category => {
        let liTag = `<li><span class="badge text-bg-light mx-1">${category}<button type="button" class="btn-transparent" onclick="removeCategory(this, '${category}')">&times;</button></span></li>`;
        ul.insertAdjacentHTML("afterbegin", liTag);
    });
    categoryInput.value = categories.toString();
}

function removeCategory(element, category) {
    let index = categories.indexOf(category);
    categories = [...categories.slice(0, index), ...categories.slice(index + 1)];
    categoryInput.value = categories.toString();
    element.parentElement.remove();
}

function addCategory(event) {
    if (event.keyCode == 32) {
        let category = event.target.value.replace(' ', '')
        if (category.length > 1 && !categories.includes(category)) {
            categories.push(category);
            createCategory();
            event.target.value = "";
        }
    } 
}

function checkInput(event) {
    if (event.keyCode == 32) {
        event.target.value = "";
    }
}