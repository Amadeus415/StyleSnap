/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/templates/**/*.html",
    "./app/static/src/**/*.{js,jsx,ts,tsx}",
    "./node_modules/flowbite/**/*.js"
  ],
  theme: {
    extend: {
      colors: {
        'brand': '#4285f4',
      }
    },
  },
  plugins: [
    require("daisyui"),
    require("flowbite/plugin")
  ],
  daisyui: {
    themes: [
      "light",
      "dark",
      "cupcake"
    ],
  },
}