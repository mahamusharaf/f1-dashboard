export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        f1: {
          red: '#E10600',
          dark: '#15151E',
          gray: '#38383F',
          light: '#F3F3F3',
          redb: '#FF1801'
        },
        tire: {
          soft: '#E10600',
          medium: '#FFB800',
          hard: '#FFFFFF',
          intermediate: '#00A046',
          wet: '#005AFF'
        }
      }
    },
  },
  plugins: [],
}
