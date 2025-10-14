# Routing

The GamePlay component uses **React Router** for client-side navigation:

- **Navigation**: Use `Link` component from `react-router-dom` for internal links
- **Route Parameters**: Access game and player info via `useParams()` hook
- **Programmatic Navigation**: Use `useNavigate()` hook for redirects
- **Pattern**: All routes use React Router for SPA behavior (no full page reloads)
