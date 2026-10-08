import { useHealthQuery } from './health.graphql.generated';

export function ApiStatus() {
  const { data, loading, error } = useHealthQuery();

  if (loading) return <p>Checking the API…</p>;
  if (error || !data) return <p role="alert">API: unreachable</p>;
  return (
    <p>
      API: {data.health.status} <small>({data.health.environment})</small>
    </p>
  );
}
