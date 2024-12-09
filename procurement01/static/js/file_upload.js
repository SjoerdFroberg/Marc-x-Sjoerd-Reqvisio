// file_upload.js

document.addEventListener('DOMContentLoaded', function() {


    // Handle remove file buttons for existing files
    document.querySelectorAll('.file-icon:not(.new-file) .remove-file-btn').forEach(function(button) {
        button.addEventListener('click', function() {
            var fileIcon = this.closest('.file-icon');
            var deleteInput = fileIcon.querySelector('input[name="delete_files"]');
            deleteInput.disabled = false; // Enable the input to mark for deletion
            fileIcon.style.display = 'none'; // Hide the file icon
        });
    });

    // File Upload Handling
    document.getElementById('upload-files-button').addEventListener('click', function() {
        document.getElementById('id_new_files').click();
    });

    // Initialize an array to keep track of new files
    let newFilesArray = [];

    // Handle file input change event
    document.getElementById('id_new_files').addEventListener('change', function() {
        var files = this.files;
        var filesContainer = document.getElementById('files-container');

        // Iterate over selected files
        for (var i = 0; i < files.length; i++) {
            var file = files[i];

            // Add the file to the newFilesArray if not already added
            if (!newFilesArray.some(f => f.name === file.name && f.lastModified === file.lastModified)) {
                newFilesArray.push(file);

                // Create file icon element
                var fileIcon = document.createElement('div');
                fileIcon.className = 'file-icon new-file';
                fileIcon.setAttribute('data-file-name', file.name);

                fileIcon.innerHTML = `
                    <button type="button" class="remove-file-btn">
                        <i class="bi bi-x-circle-fill"></i>
                    </button>
                    <div>
                        <i class="bi bi-file-earmark"></i>
                        <span>${file.name}</span>
                    </div>
                `;

                // Append the file icon to the container
                filesContainer.appendChild(fileIcon);

                // Add event listener to the remove button
                fileIcon.querySelector('.remove-file-btn').addEventListener('click', function() {
                    // Remove the file from newFilesArray
                    newFilesArray = newFilesArray.filter(f => !(f.name === file.name && f.lastModified === file.lastModified));
                    // Remove the file icon from the UI
                    fileIcon.remove();
                    // Update the file input's files property
                    updateFileInput();
                });
            }
        }

        // Update the file input's files property
        updateFileInput();
    });

    // Function to update the file input's files property
    function updateFileInput() {
        const dataTransfer = new DataTransfer();
        newFilesArray.forEach(file => {
            dataTransfer.items.add(file);
        });
        document.getElementById('id_new_files').files = dataTransfer.files;
    }


});


