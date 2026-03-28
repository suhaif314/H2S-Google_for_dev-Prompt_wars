/**
 * TriageAI — File Handler
 * Manages document (PDF) file uploads with drag-and-drop
 */

const FileHandler = {
    selectedFile: null,

    /**
     * Initialize the file handler.
     */
    init() {
        this.dropZone = document.getElementById('file-drop-zone');
        this.fileInput = document.getElementById('document-input');
        this.fileInfo = document.getElementById('doc-file-info');
        this.fileName = document.getElementById('doc-file-name');
        this.fileSize = document.getElementById('doc-file-size');
        this.fileRemove = document.getElementById('doc-file-remove');

        // Click to browse
        this.dropZone.addEventListener('click', () => this.fileInput.click());

        // File selected via input
        this.fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFile(e.target.files[0]);
            }
        });

        // Drag and drop
        this.dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.dropZone.classList.add('dragover');
        });

        this.dropZone.addEventListener('dragleave', () => {
            this.dropZone.classList.remove('dragover');
        });

        this.dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            this.dropZone.classList.remove('dragover');
            if (e.dataTransfer.files.length > 0) {
                this.handleFile(e.dataTransfer.files[0]);
            }
        });

        // Remove file
        this.fileRemove.addEventListener('click', (e) => {
            e.stopPropagation();
            this.removeFile();
        });
    },

    /**
     * Handle a selected/dropped file.
     * @param {File} file 
     */
    handleFile(file) {
        // Validate type
        if (file.type !== 'application/pdf') {
            alert('Only PDF files are supported. Please upload a PDF document.');
            return;
        }

        // Validate size (10MB max)
        const maxSize = 10 * 1024 * 1024;
        if (file.size > maxSize) {
            alert('File is too large. Maximum size is 10MB.');
            return;
        }

        this.selectedFile = file;

        // Show file info
        this.fileName.textContent = file.name;
        this.fileSize.textContent = this.formatFileSize(file.size);
        this.fileInfo.classList.remove('hidden');
        this.dropZone.classList.add('hidden');
    },

    /**
     * Remove the selected file.
     */
    removeFile() {
        this.selectedFile = null;
        this.fileInput.value = '';
        this.fileInfo.classList.add('hidden');
        this.dropZone.classList.remove('hidden');
    },

    /**
     * Format bytes to human-readable size.
     * @param {number} bytes 
     * @returns {string}
     */
    formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
    },

    /**
     * Get the selected file.
     * @returns {File|null}
     */
    getFile() {
        return this.selectedFile;
    },

    /**
     * Check if a file is selected.
     * @returns {boolean}
     */
    hasFile() {
        return this.selectedFile !== null;
    },
};
