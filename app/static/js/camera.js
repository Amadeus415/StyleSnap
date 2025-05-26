document.addEventListener('DOMContentLoaded', function() {
    const cameraButton = document.getElementById('cameraButton');
    const videoContainer = document.getElementById('videoContainer');
    const video = document.getElementById('video');
    const captureButton = document.getElementById('captureButton');
    const uploadForm = document.getElementById('uploadForm');
    const photoDataInput = document.getElementById('photoData');
    const previewContainer = document.getElementById('previewContainer');
    const photoPreview = document.getElementById('photoPreview');
    const uploadFileButton = document.getElementById('uploadFileButton');
    let stream = null;
    let canvas = null;

    // Initialize the upload button as disabled
    if (uploadFileButton) {
        uploadFileButton.disabled = true;
    }

    // Function to handle file selection and update UI
    window.showFileName = function(input) {
        const fileName = input.files[0]?.name;
        const fileNameElement = document.getElementById('fileName');
        const uploadButton = document.getElementById('uploadFileButton');
        
        if (fileName) {
            // Update text to clearly indicate photo is uploaded and next steps
            fileNameElement.textContent = `✅ Photo selected!
                                            Click the button below`;
            fileNameElement.classList.add('text-blue-700', 'font-semibold');
            
            // Make button more vibrant when photo is selected
            if (uploadButton) {
                uploadButton.disabled = false;
                uploadButton.classList.remove('bg-black', 'opacity-50');
                uploadButton.classList.add('bg-blue-600', 'hover:bg-blue-700', 'shadow-lg');
                uploadButton.innerHTML = 'Upload and Continue';
                
                
            }
        } else {
            // Reset to default state if no file selected
            fileNameElement.textContent = '';
            fileNameElement.classList.remove('text-green-600', 'font-semibold');
            
            if (uploadButton) {
                uploadButton.disabled = true;
                uploadButton.classList.add('bg-black', 'opacity-50');
                uploadButton.classList.remove('bg-blue-600', 'hover:bg-blue-700', 'shadow-lg');
                uploadButton.innerHTML = 'Upload and Continue';
            }
        }
    };

    cameraButton.addEventListener('click', async function() {
        if (!stream) {
            try {
                stream = await navigator.mediaDevices.getUserMedia({ 
                    video: { facingMode: 'user' }, 
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
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0);
        
        // Get image data as JPEG
        const imageDataUrl = canvas.toDataURL('image/jpeg', 0.8);
        
        // Log the first few characters of the base64 data for debugging
        console.log('Image data starts with:', imageDataUrl.substring(0, 50));
        
        // Update form and preview
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

    // Add form submission handler to validate data before sending
    uploadForm.addEventListener('submit', function(e) {
        const photoData = photoDataInput.value;
        if (!photoData.startsWith('data:image/jpeg;base64,')) {
            e.preventDefault();
            console.error('Invalid image data format');
            alert('Invalid image data format. Please try capturing the photo again.');
        }
    });
});