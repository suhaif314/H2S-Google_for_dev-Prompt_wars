/**
 * TriageAI — Voice Recorder
 * Handles browser audio recording using MediaRecorder API
 */

const VoiceRecorder = {
    mediaRecorder: null,
    audioChunks: [],
    audioBlob: null,
    isRecording: false,
    startTime: null,
    timerInterval: null,

    /**
     * Initialize the voice recorder.
     */
    init() {
        this.recordBtn = document.getElementById('record-btn');
        this.recordText = document.getElementById('record-text');
        this.recordIcon = document.getElementById('record-icon');
        this.waveform = document.getElementById('waveform');
        this.timer = document.getElementById('recorder-timer');
        this.fileInfo = document.getElementById('voice-file-info');
        this.fileName = document.getElementById('voice-file-name');
        this.fileRemove = document.getElementById('voice-file-remove');

        this.recordBtn.addEventListener('click', () => this.toggleRecording());
        this.fileRemove.addEventListener('click', () => this.removeRecording());
    },

    /**
     * Toggle recording on/off.
     */
    async toggleRecording() {
        if (this.isRecording) {
            this.stopRecording();
        } else {
            await this.startRecording();
        }
    },

    /**
     * Start audio recording.
     */
    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    sampleRate: 48000,
                }
            });

            this.audioChunks = [];
            this.mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus',
            });

            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };

            this.mediaRecorder.onstop = () => {
                this.audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                stream.getTracks().forEach(track => track.stop());
                this.showFileInfo();
            };

            this.mediaRecorder.start(100); // Collect data every 100ms
            this.isRecording = true;

            // UI updates
            this.recordBtn.classList.add('recording');
            this.recordText.textContent = 'Stop Recording';
            this.recordIcon.textContent = '⏹️';
            this.waveform.classList.add('active');

            // Start timer
            this.startTime = Date.now();
            this.timerInterval = setInterval(() => this.updateTimer(), 100);

        } catch (error) {
            console.error('Microphone access denied:', error);
            alert('Microphone access is required for voice recording. Please allow microphone access and try again.');
        }
    },

    /**
     * Stop recording.
     */
    stopRecording() {
        if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            this.mediaRecorder.stop();
        }

        this.isRecording = false;

        // UI updates
        this.recordBtn.classList.remove('recording');
        this.recordText.textContent = 'Start Recording';
        this.recordIcon.textContent = '🎙️';
        this.waveform.classList.remove('active');

        // Stop timer
        clearInterval(this.timerInterval);
    },

    /**
     * Update the timer display.
     */
    updateTimer() {
        const elapsed = Date.now() - this.startTime;
        const seconds = Math.floor(elapsed / 1000);
        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;
        this.timer.textContent = `${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    },

    /**
     * Show file info after recording.
     */
    showFileInfo() {
        if (this.audioBlob) {
            const sizeMB = (this.audioBlob.size / (1024 * 1024)).toFixed(2);
            this.fileName.textContent = `recording.webm (${sizeMB} MB)`;
            this.fileInfo.classList.remove('hidden');
        }
    },

    /**
     * Remove recorded audio.
     */
    removeRecording() {
        this.audioBlob = null;
        this.audioChunks = [];
        this.fileInfo.classList.add('hidden');
        this.timer.textContent = '00:00';
    },

    /**
     * Get the recorded audio blob.
     * @returns {Blob|null}
     */
    getBlob() {
        return this.audioBlob;
    },

    /**
     * Check if there's a recording available.
     * @returns {boolean}
     */
    hasRecording() {
        return this.audioBlob !== null;
    },
};
