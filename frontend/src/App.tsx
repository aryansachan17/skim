import { ApiStatus } from './features/health/ApiStatus';

export function App() {
  return (
    <main>
      <h1>Skim</h1>
      <p>Save anything, understand it in 30 seconds, find it later.</p>
      <ApiStatus />
    </main>
  );
}
