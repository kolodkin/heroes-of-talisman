import { LitElement, html, css } from 'lit'
import './styles/index.css'

class HelloWorld extends LitElement {
  render() {
    return html`
      <div class="max-w-md mx-auto bg-white rounded-xl shadow-lg p-8 text-center">
        <h1 class="text-4xl font-bold text-gray-800 mb-4">Hello World!</h1>
        <p class="text-lg text-gray-600 mb-3">Welcome to Talis Card Game</p>
        <p class="text-base text-blue-600 font-medium">Vite + Lit + TailwindCSS v4 is ready!</p>
        <div class="mt-6 space-y-2">
          <div class="px-4 py-2 bg-blue-100 text-blue-800 rounded-lg">
            ✅ Vite Development Server
          </div>
          <div class="px-4 py-2 bg-green-100 text-green-800 rounded-lg">
            ✅ Lit Web Components
          </div>
          <div class="px-4 py-2 bg-purple-100 text-purple-800 rounded-lg">
            ✅ TailwindCSS v4 Styling
          </div>
        </div>
      </div>
    `
  }
}

customElements.define('hello-world', HelloWorld)
