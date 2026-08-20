document.addEventListener("DOMContentLoaded", function () {
    if (window.lucide) {
        window.lucide.createIcons();
    }

    var photoUploads = document.querySelectorAll("[data-photo-upload]");

    photoUploads.forEach(function (upload) {
        var input = upload.querySelector('input[type="file"]');
        var dropzone = upload.querySelector(".panel-photo-dropzone");
        var count = upload.querySelector("[data-photo-count]");

        if (!input || !dropzone || !count) {
            return;
        }

        var updateCount = function () {
            var total = input.files ? input.files.length : 0;

            if (total === 0) {
                count.textContent = "Nenhuma foto selecionada";
                return;
            }

            count.textContent = total === 1 ? "1 foto selecionada" : total + " fotos selecionadas";
        };

        ["dragenter", "dragover"].forEach(function (eventName) {
            dropzone.addEventListener(eventName, function (event) {
                event.preventDefault();
                event.stopPropagation();
                dropzone.classList.add("is-dragging");
            });
        });

        ["dragleave", "drop"].forEach(function (eventName) {
            dropzone.addEventListener(eventName, function (event) {
                event.preventDefault();
                event.stopPropagation();
                dropzone.classList.remove("is-dragging");
            });
        });

        dropzone.addEventListener("drop", function (event) {
            var files = event.dataTransfer && event.dataTransfer.files;

            if (!files || files.length === 0) {
                return;
            }

            input.files = files;
            input.dispatchEvent(new Event("change", { bubbles: true }));
        });

        input.addEventListener("change", updateCount);
        updateCount();
    });
});
