import { LitElement, html, css } from 'lit'
import './styles/index.css'
import { SignalWatcher } from '@lit-labs/preact-signals'
import {
  testSignals,
  isAuthenticated,
  currentUser,
  authError,
  isLoading
} from './services/auth.js'

class HelloWorld extends SignalWatcher(LitElement) {
  // No need for manual signal watching with the official integration
  // Signals are automatically tracked when accessed in render()

  render() {
    return html`
      <div class="max-w-2xl mx-auto bg-white rounded-xl shadow-lg p-8 text-center">
        <h1 class="text-4xl font-bold text-gray-800 mb-4">Hello World!</h1>
        <p class="text-lg text-gray-600 mb-3">Welcome to Talis Card Game</p>
        <p class="text-base text-blue-600 font-medium">Vite + Lit + TailwindCSS v4 + Signals is ready!</p>

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
          <div class="px-4 py-2 bg-orange-100 text-orange-800 rounded-lg">
            ✅ @preact/signals State Management
          </div>
        </div>

        <!-- Signal Testing Section -->
        <div class="mt-8 p-6 bg-gray-50 rounded-lg">
          <h2 class="text-2xl font-semibold text-gray-800 mb-4">Signal Testing</h2>

          <div class="space-y-4">
            <!-- Counter Signal Test -->
            <div class="p-4 bg-white rounded-lg shadow-sm">
              <h3 class="font-semibold text-gray-700 mb-2">Counter Signal</h3>
              <p class="text-lg font-mono text-blue-600 mb-3">
                Count: ${testSignals.counter.value}
              </p>
              <button
                @click=${this._incrementCounter}
                class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
              >
                Increment Counter
              </button>
            </div>

            <!-- Message Signal Test -->
            <div class="p-4 bg-white rounded-lg shadow-sm">
              <h3 class="font-semibold text-gray-700 mb-2">Message Signal</h3>
              <p class="text-lg text-green-600 mb-3">
                "${testSignals.message.value}"
              </p>
              <button
                @click=${this._updateMessage}
                class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 transition-colors"
              >
                Update Message
              </button>
            </div>

            <!-- Auth Status -->
            <div class="p-4 bg-white rounded-lg shadow-sm">
              <h3 class="font-semibold text-gray-700 mb-2">Auth Status</h3>
              <div class="space-y-2">
                <p class="text-sm">
                  <span class="font-medium">Authenticated:</span>
                  <span class="${isAuthenticated.value ? 'text-green-600' : 'text-red-600'}">
                    ${isAuthenticated.value ? 'Yes' : 'No'}
                  </span>
                </p>
                <p class="text-sm">
                  <span class="font-medium">Loading:</span>
                  <span class="${isLoading.value ? 'text-yellow-600' : 'text-gray-600'}">
                    ${isLoading.value ? 'Yes' : 'No'}
                  </span>
                </p>
                ${authError.value ? html`
                  <p class="text-sm text-red-600">
                    <span class="font-medium">Error:</span> ${authError.value}
                  </p>
                ` : ''}
              </div>
            </div>
          </div>
        </div>
      </div>
    `
  }

  _incrementCounter() {
    testSignals.increment()
  }

  _updateMessage() {
    const messages = [
      'Hello from signals!',
      'Signals are reactive!',
      'Auto-updating components!',
      'State management made easy!',
      'Preact signals + Lit = ❤️'
    ]
    const randomMessage = messages[Math.floor(Math.random() * messages.length)]
    testSignals.updateMessage(randomMessage)
  }
}

customElements.define('hello-world', HelloWorld)
