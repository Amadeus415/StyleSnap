
 document.addEventListener('DOMContentLoaded', function() {
    const cameraButton = document.getElementById('cameraButton');
    let stream = null;
    let videoElement = null;
    let canvas = null;

    cameraButton.addEventListener('click', async function() {
        // If video element doesn't exist, create it and start camera
        if (!videoElement) {
            videoElement = document.createElement('video');
            videoElement.setAttribute('playsinline', '');
            videoElement.setAttribute('autoplay', '');
            document.body.appendChild(videoElement);

            // Create capture button
            const captureButton = document.createElement('button');
            captureButton.textContent = 'Take Photo';
            document.body.appendChild(captureButton);

            // Create canvas for photo capture
            canvas = document.createElement('canvas');
            document.body.appendChild(canvas);

            try {
                stream = await navigator.mediaDevices.getUserMedia({ 
                    video: { facingMode: 'environment' }, 
                    audio: false 
                });
                videoElement.srcObject = stream;

                // Add click handler for capture button
                captureButton.addEventListener('click', function() {
                    // Set canvas dimensions to match video
                    canvas.width = videoElement.videoWidth;
                    canvas.height = videoElement.videoHeight;
                    
                    // Draw video frame to canvas
                    canvas.getContext('2d').drawImage(videoElement, 0, 0);
                    
                    // Convert to data URL and create download link
                    const imageDataUrl = canvas.toDataURL('image/jpeg');
                    const downloadLink = document.createElement('a');
                    downloadLink.href = imageDataUrl;
                    downloadLink.download = 'photo.jpg';
                    downloadLink.textContent = 'Download Photo';
                    document.body.appendChild(downloadLink);
                });
            } catch (err) {
                console.error('Error accessing camera:', err);
            }
        } else {
            // Stop camera and remove elements if already running
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
            videoElement.remove();
            canvas.remove();
            document.querySelectorAll('button, a').forEach(el => {
                if (el !== cameraButton) el.remove();
            });
            videoElement = null;
            canvas = null;
            stream = null;
        }
    });
});
