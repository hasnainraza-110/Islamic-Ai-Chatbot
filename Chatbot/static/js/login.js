document.querySelectorAll('.toggle-password').forEach(item => {
    item.addEventListener('click', function () {
        let input = this.previousElementSibling;
        if (input.type === "password") {
            input.type = "text";
        } else {
            input.type = "password";
        }
    });
});
