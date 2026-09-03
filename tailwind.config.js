module.exports = {
  darkMode: 'class',
  content: [
    "./static/**/*.html",
    "./static/**/*.js"
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#fff0f4',
          100: '#ffe4ec',
          200: '#fecddc',
          300: '#fea3c0',
          400: '#fc6b98',
          500: '#ff5c8a',
          600: '#e11d61',
          700: '#be124e',
          800: '#9e1244',
          900: '#84133d',
        },
        gold: {
          400: '#e4ccad',
          500: '#c5a880',
          600: '#a38458',
        }
      },
      fontFamily: {
        display: ['"Syne"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        serif: ['"Shippori Mincho"', '"Cinzel"', 'ui-serif', 'Georgia', 'serif'],
        sans: ['"Plus Jakarta Sans"', 'ui-sans-serif', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
      }
    }
  },
  plugins: []
}
