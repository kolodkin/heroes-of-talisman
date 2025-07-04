import { LitElement, html, css } from 'lit'

class HelloWorld extends LitElement {
  static styles = css`
    :host {
      display: block;
      padding: 2rem;
      text-align: center;
      font-family: Arial, sans-serif;
    }

    h1 {
      color: #333;
      margin-bottom: 1rem;
    }

    p {
      color: #666;
      font-size: 1.2rem;
    }
  `

  render() {
    return html`
      <h1>Hello World!</h1>
      <p>Welcome to Talis Card Game</p>
      <p>Vite + Lit development environment is ready!</p>
    `
  }
}

customElements.define('hello-world', HelloWorld)
