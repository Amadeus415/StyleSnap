# StyleSnap
* Input: Photo of your current outfit
* Output: Style score, outfit suggestions, and color coordination advice
* Monetization: Affiliate links to clothing stores, premium features

# Tech Stack
1. frontend: html, tailwindcss
2. Camera: Javascript
3. Backend: Flask
4. Storeage: ??AWS S3
5. Auth: Google auth
6. AI: xAI api
7. Products: Amazon Prod Adv API

# To do:
1. Setup & Infrastructure
   - [x] Add upload from folder functionality
   - [x] Some kind of storage cleanup
   - [ ] clean product screen
   - [ ] mobile tests
   - [ ] Add max file size
   - [ ] x

2. AI API
   - [ ] Map out plan for AI system
   - [ ] add into app utility

3. Potential Prolblems
 - [] storeage cleanup with simaltaneous users
    - Solution: switch to S3 with automatic cleanup every day
    - Or use scheduler 