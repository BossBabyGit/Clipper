export const API = "http://localhost:8000";

export const uploadVideo = file => {
  const f = new FormData();
  f.append("file", file);
  return fetch(`${API}/upload`, { method: "POST", body: f });
};

export const getClips = () => fetch(`${API}/clips`).then(r => r.json());

export const getStatus = () => fetch(`${API}/status`).then(r => r.json());
