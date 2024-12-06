document.addEventListener('DOMContentLoaded', function() {
    const cameraButton = document.getElementById('cameraButton');
    const uploadForm = document.getElementById('uploadForm');
    const photoDataInput = document.getElementById('photoData');
    const uploadButton = document.getElementById('uploadButton');
    const previewContainer = document.getElementById('previewContainer');
    const photoPreview = document.getElementById('photoPreview');
    let stream = null;
    let videoElement = null;
    let canvas = null;

    cameraButton.addEventListener('click', async function() {
        if (!videoElement) {
            videoElement = document.createElement('video');
            videoElement.setAttribute('playsinline', '');
            videoElement.setAttribute('autoplay', '');
            document.body.appendChild(videoElement);

            const captureButton = document.createElement('button');
            captureButton.textContent = 'Take Photo';
            document.body.appendChild(captureButton);

            canvas = document.createElement('canvas');

            try {
                stream = await navigator.mediaDevices.getUserMedia({ 
                    video: { facingMode: 'environment' }, 
                    audio: false 
                });
                videoElement.srcObject = stream;

                captureButton.addEventListener('click', function() {
                    canvas.width = videoElement.videoWidth;
                    canvas.height = videoElement.videoHeight;
                    canvas.getContext('2d').drawImage(videoElement, 0, 0);
                    
                    // Get image data and update preview
                    const imageDataUrl = canvas.toDataURL('image/jpeg');
                    photoDataInput.value = imageDataUrl;
                    photoPreview.src = imageDataUrl;
                    
                    // Show preview and upload form
                    previewContainer.style.display = 'block';
                    uploadForm.style.display = 'block';
                    
                    // Stop camera and cleanup
                    if (stream) {
                        stream.getTracks().forEach(track => track.stop());
                    }
                    videoElement.remove();
                    captureButton.remove();
                    videoElement = null;
                });
            } catch (err) {
                console.error('Error accessing camera:', err);
            }
        } else {
            // Reset everything
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
            videoElement.remove();
            document.querySelectorAll('button').forEach(el => {
                if (el !== cameraButton && el !== uploadButton) el.remove();
            });
            videoElement = null;
            canvas = null;
            stream = null;
            uploadForm.style.display = 'none';
            previewContainer.style.display = 'none';
            photoDataInput.value = '';
            photoPreview.src = '';
        }
    });
});