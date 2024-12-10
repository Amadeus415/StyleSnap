document.addEventListener('DOMContentLoaded', function() {
    const cameraButton = document.getElementById('cameraButton');
    const videoContainer = document.getElementById('videoContainer');
    const video = document.getElementById('video');
    const captureButton = document.getElementById('captureButton');
    const uploadForm = document.getElementById('uploadForm');
    const photoDataInput = document.getElementById('photoData');
    const previewContainer = document.getElementById('previewContainer');
    const photoPreview = document.getElementById('photoPreview');
    let stream = null;
    let canvas = null;

    cameraButton.addEventListener('click', async function() {
        if (!stream) {
            try {
                stream = await navigator.mediaDevices.getUserMedia({ 
                    video: { facingMode: 'environment' }, 
                    audio: false 
                });
                video.srcObject = stream;
                videoContainer.classList.remove('hidden');
                cameraButton.textContent = 'Close Camera';
                
                // Hide preview and form if showing
                previewContainer.classList.add('hidden');
                uploadForm.classList.add('hidden');
            } catch (err) {
                console.error('Error accessing camera:', err);
            }
        } else {
            // Stop camera and reset UI
            stream.getTracks().forEach(track => track.stop());
            stream = null;
            videoContainer.classList.add('hidden');
            cameraButton.textContent = 'Open Camera';
        }
    });

    captureButton.addEventListener('click', function() {
        if (!canvas) {
            canvas = document.createElement('canvas');
        }
        
        // Set canvas dimensions to match video
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        // Draw video frame to canvas
        canvas.getContext('2d').drawImage(video, 0, 0);
        
        // Get image data and update preview
        const imageDataUrl = canvas.toDataURL('image/jpeg');
        photoDataInput.value = imageDataUrl;
        photoPreview.src = imageDataUrl;
        
        // Show preview and upload form
        previewContainer.classList.remove('hidden');
        uploadForm.classList.remove('hidden');
        
        // Stop camera and hide video
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        }
        videoContainer.classList.add('hidden');
        cameraButton.textContent = 'Open Camera';
    });
});