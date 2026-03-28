/**
 * TriageAI — Main Application Logic
 * Orchestrates UI, input handling, and results display
 */

document.addEventListener('DOMContentLoaded', () => {
    // Initialize modules
    VoiceRecorder.init();
    FileHandler.init();

    // --- DOM Elements ---
    const tabs = document.querySelectorAll('.tab-btn');
    const panels = document.querySelectorAll('.tab-panel');
    const textArea = document.getElementById('emergency-text');
    const charCount = document.getElementById('char-count');
    const locationInput = document.getElementById('location-input');
    const analyzeBtn = document.getElementById('analyze-btn');
    const analyzeBtnText = document.querySelector('.analyze-btn-text');
    const analyzeSpinner = document.getElementById('analyze-spinner');
    const inputSection = document.getElementById('input-section');
    const resultsSection = document.getElementById('results-section');
    const newReportBtn = document.getElementById('new-report-btn');
    const errorBanner = document.getElementById('error-banner');
    const errorMessage = document.getElementById('error-message');
    const errorClose = document.getElementById('error-close');
    const statusDot = document.getElementById('status-dot');
    const statusText = document.getElementById('status-text');

    // --- Tab Switching ---
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetPanel = tab.dataset.tab;

            tabs.forEach(t => t.classList.remove('active'));
            panels.forEach(p => p.classList.remove('active'));

            tab.classList.add('active');
            document.getElementById(`panel-${targetPanel}`).classList.add('active');
        });
    });

    // --- Character Counter ---
    textArea.addEventListener('input', () => {
        charCount.textContent = textArea.value.length;
    });

    // --- Error Handling ---
    function showError(message) {
        errorMessage.textContent = message;
        errorBanner.classList.remove('hidden');
        statusDot.classList.add('error');
        statusDot.classList.remove('processing');
        statusText.textContent = 'Error';

        setTimeout(() => {
            errorBanner.classList.add('hidden');
            statusDot.classList.remove('error');
            statusText.textContent = 'System Ready';
        }, 10000);
    }

    errorClose.addEventListener('click', () => {
        errorBanner.classList.add('hidden');
        statusDot.classList.remove('error');
        statusText.textContent = 'System Ready';
    });

    // --- Submit Analysis ---
    analyzeBtn.addEventListener('click', async () => {
        const text = textArea.value.trim();
        const location = locationInput.value.trim();
        const voiceBlob = VoiceRecorder.getBlob();
        const documentFile = FileHandler.getFile();

        // Validate at least one input
        if (!text && !voiceBlob && !documentFile) {
            showError('Please provide at least one input: text description, voice recording, or PDF document.');
            return;
        }

        // Start loading state
        analyzeBtn.disabled = true;
        analyzeBtnText.classList.add('hidden');
        analyzeSpinner.classList.remove('hidden');
        statusDot.classList.add('processing');
        statusText.textContent = 'Processing...';
        errorBanner.classList.add('hidden');

        try {
            const response = await API.submitTriage({
                text: text || null,
                location: location || null,
                voiceBlob,
                documentFile,
            });

            if (response.success && response.report) {
                displayResults(response);
            } else {
                showError(response.error || 'Analysis failed. Please try again.');
            }
        } catch (error) {
            console.error('Triage submission error:', error);
            showError(error.message || 'Failed to connect to the server. Please check your connection.');
        } finally {
            analyzeBtn.disabled = false;
            analyzeBtnText.classList.remove('hidden');
            analyzeSpinner.classList.add('hidden');
            statusDot.classList.remove('processing');
            statusText.textContent = 'System Ready';
        }
    });

    // --- Display Results ---
    function displayResults(response) {
        const report = response.report;

        // Show results, hide input
        inputSection.classList.add('hidden');
        resultsSection.classList.remove('hidden');

        // Processing time
        document.getElementById('processing-time').textContent =
            `⚡ ${(response.processing_time_ms / 1000).toFixed(1)}s`;

        // Severity
        const severityScore = report.severity?.score || 3;
        const severityLabels = {
            1: 'MINOR', 2: 'MODERATE', 3: 'SERIOUS', 4: 'CRITICAL', 5: 'LIFE-THREATENING'
        };

        const severityBanner = document.getElementById('severity-banner');
        severityBanner.className = `severity-banner severity-${severityScore}`;
        document.getElementById('severity-score').textContent = severityScore;
        document.getElementById('severity-label').textContent = severityLabels[severityScore] || 'UNKNOWN';
        document.getElementById('severity-justification').textContent =
            report.severity?.justification || 'No justification available.';

        // Summary
        document.getElementById('incident-type').textContent = report.incident_type || 'UNKNOWN';
        document.getElementById('summary-text').textContent = report.summary || 'No summary available.';

        // Extracted Details
        const details = report.extracted_details || {};
        document.getElementById('detail-location').textContent = details.location || 'Unknown';
        document.getElementById('detail-affected').textContent = details.num_affected || 'Unknown';
        document.getElementById('detail-caller-state').textContent =
            (details.caller_emotional_state || 'unknown').toUpperCase();

        // Injuries tags
        const injuriesContainer = document.getElementById('detail-injuries');
        injuriesContainer.innerHTML = '';
        (details.injuries_described || []).forEach(injury => {
            const tag = document.createElement('span');
            tag.className = 'detail-tag';
            tag.textContent = injury;
            injuriesContainer.appendChild(tag);
        });
        if (!details.injuries_described?.length) {
            injuriesContainer.innerHTML = '<span class="detail-tag">None reported</span>';
        }

        // Hazards tags
        const hazardsContainer = document.getElementById('detail-hazards');
        hazardsContainer.innerHTML = '';
        (details.hazards_present || []).forEach(hazard => {
            const tag = document.createElement('span');
            tag.className = 'detail-tag hazard';
            tag.textContent = hazard;
            hazardsContainer.appendChild(tag);
        });
        if (!details.hazards_present?.length) {
            hazardsContainer.innerHTML = '<span class="detail-tag">None identified</span>';
        }

        // Immediate Actions
        const actionsList = document.getElementById('actions-list');
        actionsList.innerHTML = '';
        (report.immediate_actions || []).forEach(action => {
            const li = document.createElement('li');
            li.className = 'action-item';
            li.innerHTML = `
                <div class="action-priority">${action.priority}</div>
                <div class="action-content">
                    <div class="action-text">${action.action}</div>
                    <div class="action-responsible">→ ${action.responsible_party}</div>
                </div>
            `;
            actionsList.appendChild(li);
        });

        // Resources
        const resources = report.resources_needed || {};
        const resourcesGrid = document.getElementById('resources-grid');
        resourcesGrid.innerHTML = `
            <div class="resource-item">
                <div class="resource-count">${resources.ambulances || 0}</div>
                <div class="resource-label">🚑 Ambulances</div>
            </div>
            <div class="resource-item">
                <div class="resource-count">${resources.fire_trucks || 0}</div>
                <div class="resource-label">🚒 Fire Trucks</div>
            </div>
            <div class="resource-item">
                <div class="resource-count">${resources.police_units || 0}</div>
                <div class="resource-label">🚔 Police Units</div>
            </div>
        `;

        const specializedContainer = document.getElementById('specialized-resources');
        specializedContainer.innerHTML = '';
        (resources.specialized || []).forEach(item => {
            const tag = document.createElement('span');
            tag.className = 'specialized-tag';
            tag.textContent = item;
            specializedContainer.appendChild(tag);
        });

        // Weather Context
        const weatherCard = document.getElementById('weather-card');
        const weatherBody = document.getElementById('weather-body');
        if (report.weather_context) {
            weatherCard.classList.remove('hidden');
            const wc = report.weather_context;
            let weatherHTML = '<div class="weather-info">';
            if (wc.temperature) weatherHTML += `<div class="weather-item"><strong>🌡️ Temp:</strong> ${wc.temperature}</div>`;
            if (wc.conditions) weatherHTML += `<div class="weather-item"><strong>☁️ Conditions:</strong> ${wc.conditions}</div>`;
            if (wc.wind_speed) weatherHTML += `<div class="weather-item"><strong>💨 Wind:</strong> ${wc.wind_speed}</div>`;
            (wc.alerts || []).forEach(alert => {
                weatherHTML += `<div class="weather-alert">⚠️ ${alert}</div>`;
            });
            weatherHTML += '</div>';
            weatherBody.innerHTML = weatherHTML;
        } else {
            weatherCard.classList.add('hidden');
        }

        // News Context
        const newsCard = document.getElementById('news-card');
        const newsBody = document.getElementById('news-body');
        if (report.news_context?.related_incidents?.length) {
            newsCard.classList.remove('hidden');
            newsBody.innerHTML = report.news_context.related_incidents
                .map(item => `<div class="news-item">${item}</div>`)
                .join('');
        } else {
            newsCard.classList.add('hidden');
        }

        // Recommended Facility
        const facility = report.recommended_facility || {};
        document.getElementById('facility-type').textContent = facility.type || 'Hospital';
        document.getElementById('facility-reason').textContent = facility.reason || 'General medical facility';

        // Input Sources
        const sourcesBadges = document.getElementById('sources-badges');
        sourcesBadges.innerHTML = '';
        (report.input_sources || []).forEach(source => {
            const badge = document.createElement('span');
            badge.className = 'source-badge';
            badge.textContent = source.toUpperCase();
            sourcesBadges.appendChild(badge);
        });

        // Confidence
        const confidence = report.confidence_score || 0.7;
        const confidencePercent = Math.round(confidence * 100);
        document.getElementById('confidence-fill').style.width = `${confidencePercent}%`;
        document.getElementById('confidence-value').textContent = `${confidencePercent}%`;

        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    // --- New Report ---
    newReportBtn.addEventListener('click', () => {
        resultsSection.classList.add('hidden');
        inputSection.classList.remove('hidden');

        // Clear inputs
        textArea.value = '';
        charCount.textContent = '0';
        locationInput.value = '';
        VoiceRecorder.removeRecording();
        FileHandler.removeFile();

        inputSection.scrollIntoView({ behavior: 'smooth' });
    });

    // --- Health Check ---
    (async () => {
        try {
            await API.healthCheck();
            statusDot.classList.remove('error');
            statusText.textContent = 'System Ready';
        } catch {
            statusDot.classList.add('error');
            statusText.textContent = 'Server Offline';
        }
    })();
});
