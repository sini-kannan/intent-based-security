const API_BASE_URL = 'http://localhost:8000/api';

export interface Intent {
  id: string;
  text: string;
  container_name: string;
  yaml_content: string;
  created_at: string;
}

export const createIntent = async (text: string, containerName: string) => {
  const response = await fetch(`${API_BASE_URL}/intents/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, container_name: containerName })
  });
  if (!response.ok) throw new Error('Failed to create intent');
  return response.json();
};

export const listIntents = async () => {
  const response = await fetch(`${API_BASE_URL}/intents/`);
  if (!response.ok) throw new Error('Failed to list intents');
  return response.json();
};

export const triggerPipeline = async () => {
  const response = await fetch(`${API_BASE_URL}/run_pipeline`, { method: 'POST' });
  if (!response.ok) throw new Error('Pipeline failed');
  return response.json();
};

export const getDriftLogs = async () => {
  const response = await fetch(`${API_BASE_URL}/drift`);
  if (!response.ok) throw new Error('Failed to get drift logs');
  return response.json();
};

export const getContainers = async () => {
  const response = await fetch(`${API_BASE_URL}/containers`);
  if (!response.ok) throw new Error('Failed to get containers');
  return response.json();
};

export const getPolicies = async () => {
  const response = await fetch(`${API_BASE_URL}/policies`);
  if (!response.ok) throw new Error('Failed to get policies');
  return response.json();
};
