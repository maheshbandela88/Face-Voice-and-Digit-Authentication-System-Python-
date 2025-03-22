class Authenticator {
    constructor() {
        this.videoStream = null;
        this.isProcessing = false;
        this.mediaRecorder = null;
    }

    setButtonState(buttonId, isLoading) {
        const btn = document.getElementById(buttonId);
        if (!btn) return;

        this.isProcessing = isLoading;
        btn.disabled = isLoading;
        btn.classList.toggle('processing', isLoading);
        btn.innerText = isLoading ? "Processing..." : this.getButtonText(buttonId);
    }

    getButtonText(buttonId) {
        return {
            'pin-btn': 'Proceed',
            'face-btn': 'Verify Identity',
            'voice-btn': 'Begin Voice Authentication'
        }[buttonId] || 'Submit';
    }

    showError(elementId, message) {
        const error = document.getElementById(elementId);
        if (!error) return;

        error.innerText = message;
        error.classList.add('show');
        setTimeout(() => error.classList.remove('show'), 5000);
    }

    async sendRequest(url, method, body = null, isJson = true) {
        try {
            const headers = { "Accept": "application/json" };
            if (isJson) headers["Content-Type"] = "application/json";

            const options = {
                method,
                headers,
                mode: 'cors',
                credentials: 'omit'
            };

            if (body) options.body = isJson ? JSON.stringify(body) : body;

            const response = await fetch(url, options);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(`Server error: ${response.status} - ${data.message || "Unknown error"}`);
            }

            return data;
        } catch (error) {
            console.error(`Request to ${url} failed:`, error);
            this.showError("error", error.message.includes("Failed to fetch") 
                ? "Server unreachable. Ensure backend is running."
                : error.message);
            return null;
        }
    }

    async validatePIN() {
        if (this.isProcessing) return;

        const pin = document.getElementById("pin")?.value;
        if (!pin) {
            this.showError("error", "Please enter a PIN");
            return;
        }

        this.setButtonState("pin-btn", true);
        const data = await this.sendRequest("http://127.0.0.1:5000/validate-pin", "POST", { pin });

        if (data?.success) {
            window.location.href = "face.html";
        } else {
            this.showError("error", data?.message || "Incorrect PIN");
        }

        this.setButtonState("pin-btn", false);
    }

    async captureFace() {
        if (this.isProcessing || !this.videoStream) return;

        const video = document.getElementById("video");
        if (!video) {
            this.showError("error", "Camera not available");
            return;
        }

        this.setButtonState("face-btn", true);
        const canvas = document.createElement("canvas");
        const context = canvas.getContext("2d");

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        const imageData = canvas.toDataURL("image/jpeg");
        console.log("Captured Image Data:", imageData.substring(0, 50));

        if (!imageData || imageData.length < 50) {
            this.showError("error", "Failed to capture valid image");
            this.setButtonState("face-btn", false);
            return;
        }

        const data = await this.sendRequest("http://127.0.0.1:5000/face-auth", "POST", { image: imageData });

        if (data?.success) {
            this.stopVideoStream();
            window.location.href = "voice.html";
        } else {
            this.showError("error", data?.message || "Face verification failed");
        }

        this.setButtonState("face-btn", false);
    }

    async startRecording() {
        if (this.isProcessing) return;

        this.setButtonState("voice-btn", true);
        const micVisualizer = document.querySelector('.mic-visualizer');
        micVisualizer?.classList.add('active');

        try {
            // Simply call the /voice-auth endpoint, which will handle voice capture on the server
            const data = await this.sendRequest("http://127.0.0.1:5000/voice-auth", "POST", null, false);

            if (data?.success) {
                window.location.href = "success.html";
            } else {
                // More specific error messages based on the server's response
                let errorMessage = "Voice verification failed";
                if (data?.message) {
                    if (data.message.includes("No backend available")) {
                        errorMessage = "Voice recognition failed: No backend available. Ensure the server has internet and 'flac' installed.";
                    } else if (data.message.includes("No internet connection")) {
                        errorMessage = "Voice recognition failed: No internet connection on the server.";
                    } else if (data.message.includes("Incorrect voice PIN")) {
                        errorMessage = "Voice verification failed: Incorrect voice PIN. Please try again.";
                    } else if (data.message.includes("Could not understand audio")) {
                        errorMessage = "Voice verification failed: Could not understand the audio. Please speak clearly.";
                    } else if (data.message.includes("Maximum attempts reached")) {
                        errorMessage = "Voice verification failed: Maximum attempts reached. Access denied.";
                    } else {
                        errorMessage = data.message;
                    }
                }
                this.showError("error", errorMessage);
            }
        } catch (error) {
            console.error("Voice Auth Error:", error);
            this.showError("error", "Voice authentication failed: Server error");
        } finally {
            this.setButtonState("voice-btn", false);
            micVisualizer?.classList.remove('active');
        }
    }

    async initWebcam() {
        const video = document.getElementById("video");
        if (!video) return;

        try {
            this.videoStream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = this.videoStream;
        } catch (error) {
            console.error("Webcam Error:", error);
            this.showError("error", "Camera access denied");
        }
    }

    stopVideoStream() {
        if (this.videoStream) {
            this.videoStream.getTracks().forEach(track => track.stop());
            this.videoStream = null;
        }
    }

    stopAudioStream(stream) {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
    }
}

const auth = new Authenticator();

document.addEventListener("DOMContentLoaded", () => {
    auth.initWebcam();
    window.validatePIN = () => auth.validatePIN();
    window.captureFace = () => auth.captureFace();
    window.startRecording = () => auth.startRecording();
});