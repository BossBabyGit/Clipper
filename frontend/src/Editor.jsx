import { uploadVideo, getClips } from "./api";
import { useState } from "react";

export default function Editor() {
  const [clips, setClips] = useState([]);

  async function handleUpload(file) {
    await uploadVideo(file);
    const c = await getClips();
    setClips(c);
  }

  return (
    <div>
      <h2>Upload VOD</h2>
      <input type="file" accept="video/mp4"
        onChange={e => handleUpload(e.target.files[0])}
      />

      <h3>Detected Clips</h3>
      <ul>
        {clips.map(c => <li key={c}>{c}</li>)}
      </ul>
    </div>
  );
}
