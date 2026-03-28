/**
 * TriageAI — API Communication Layer
 * Handles all HTTP requests to the backend
 */

const API = {
    BASE_URL: window.location.origin,

    /**
     * Send multimodal triage request to the backend.
     * @param {Object} params
     * @param {string} [params.text] - Text description
     * @param {string} [params.location] - Location string
     * @param {Blob} [params.voiceBlob] - Recorded audio blob
     * @param {File} [params.documentFile] - PDF file
     * @returns {Promise<Object>} Triage response
     */
    async submitTriage({ text, location, voiceBlob, documentFile }) {
        const formData = new FormData();

        if (text && text.trim()) {
            formData.append('text', text.trim());
        }

        if (location && location.trim()) {
            formData.append('location', location.trim());
        }

        if (voiceBlob) {
            formData.append('voice_file', voiceBlob, 'recording.webm');
        }

        if (documentFile) {
            formData.append('document_file', documentFile);
        }

        const response = await fetch(`${this.BASE_URL}/api/triage`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Server error: ${response.status}`);
        }

        return response.json();
    },

    /**
     * Check backend health.
     * @returns {Promise<Object>}
     */
    async healthCheck() {
        const response = await fetch(`${this.BASE_URL}/api/health`);
        return response.json();
    },

    /**
     * List all triage reports.
     * @returns {Promise<Object>}
     */
    async listReports() {
        const response = await fetch(`${this.BASE_URL}/api/reports`);
        return response.json();
    },

    /**
     * Get a specific triage report.
     * @param {string} incidentId 
     * @returns {Promise<Object>}
     */
    async getReport(incidentId) {
        const response = await fetch(`${this.BASE_URL}/api/reports/${incidentId}`);
        if (!response.ok) throw new Error('Report not found');
        return response.json();
    },
};
