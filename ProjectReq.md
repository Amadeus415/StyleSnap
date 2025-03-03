# StyleSnap
* Input: Seflie Photo of yourself
* Output: Attractiveness Rank, Potential Attractiveness, Look maximization advice(skin, hair, jawline, confidence), as well as amazon products to Look Maximize

*User value: User sumbits photo, gets their attractiveness, and how to improve their looks
* Ethos: trained on data from health profesionals: huberman etc...

# Tech Stack
1. frontend: html, tailwindcss
2. Camera: Javascript
3. Backend: Flask
4. Storeage: AWS S3
5. Auth: Google auth
6. AI: Goiogle Gemini
7. Products: Amazon Prod Adv API
8. DB: Python SQL Lite
9. Payment: Stripe

# App Flow
1. Landing.html - Sells the user on product, getting them to press "Get Scan"
2. Camera.html - Take photo with camera, or upload photo
3. Results.html - Show user Score, with other scores and potential score hidden
   * Goal: get user press "continue with google"
4. Paypage.html - Mayke payment to continue
5. Dashboard.html - Main page, giving user value on how to increase their score

