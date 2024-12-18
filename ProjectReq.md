# StyleSnap
* Input: Photo of your current outfit
* Output: Style score, outfit suggestions, and color coordination advice
* Monetization: Affiliate links to Amazon products, Pay to see Rating

# Tech Stack
1. frontend: html, tailwindcss
2. Camera: Javascript
3. Backend: Flask
4. Storeage: ??AWS S3
5. Auth: Google auth
6. AI: xAI api
7. Products: Amazon Prod Adv API
8. DB: SQL Lite
9. Payment: Stripe

# App Flow
1. Landing.html - Sells the user on product, getting them to press "Get Scan"
2. Camera.html - Take photo with camera, or upload photo
3. Results.html - Show user Score, with other scores and potential score hidden
   * Goal: get user press "continue with google"
4. Paypage.html - Mayke payment to continue
5. Dashboard.html - Main page, giving user value on how to increase their score

# To do:
1. Setup & Infrastructure
   - [x] Add upload from folder functionality
   - [x] Some kind of storage cleanup
   - [ ] Add max file size
   - [ ] x

2. AI API
   - [ ] Improve the Prompt
   - [x] Map out plan for AI system
   - [x] add into app utility

3. Potential Prolblems
 - [] storeage cleanup with simaltaneous users
    - Solution: switch to S3 with scheduled cleanup

 - [] Save progress before implementing sqllite, and s3


4. Future
   - [ ] Look into model improvement