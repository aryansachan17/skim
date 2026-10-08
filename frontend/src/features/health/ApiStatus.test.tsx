import { MockedProvider } from '@apollo/client/testing';
import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { ApiStatus } from './ApiStatus';
import { HealthDocument } from './health.graphql.generated';

describe('ApiStatus', () => {
  it('shows the API status once the health query succeeds', async () => {
    const mocks = [
      {
        request: { query: HealthDocument },
        result: {
          data: {
            health: {
              __typename: 'Health',
              status: 'ok',
              environment: 'staging',
              version: '4f2c9e1a8b7d6c5e',
            },
          },
        },
      },
    ];

    render(
      <MockedProvider mocks={mocks}>
        <ApiStatus />
      </MockedProvider>,
    );

    expect(screen.getByText('Checking the API…')).toBeInTheDocument();
    expect(await screen.findByText(/API: ok/)).toBeInTheDocument();
    expect(screen.getByText('(staging, 4f2c9e1)')).toBeInTheDocument();
  });

  it('tells the user when the API cannot be reached', async () => {
    const mocks = [{ request: { query: HealthDocument }, error: new Error('Network down') }];

    render(
      <MockedProvider mocks={mocks}>
        <ApiStatus />
      </MockedProvider>,
    );

    expect(await screen.findByRole('alert')).toHaveTextContent('API: unreachable');
  });
});
