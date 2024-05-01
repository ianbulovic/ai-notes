import axios from "axios";

import { API_URL } from "./constants";

export async function getHealth() {
  try {
    const response = await axios.get(`${API_URL}/health`);
    return response.data;
  } catch (error) {
    return false;
  }
}

// ----- Notes API ----- //

export async function getNotes(
  query = null,
  sortBy = "opened",
  tags = [],
  resultsPerPage = 10,
  pageNumber = 1
) {
  let url = `${API_URL}/notes?`;
  if (query) {
    url = url + `q=${query}&`;
  }
  if (sortBy) {
    url = url + `sort=${sortBy}&`;
  }
  if (tags.length > 0) {
    url = url + `tags=${tags.map((tag) => tag.id).join(",")}&`;
  }
  url = url + `n=${resultsPerPage}&page=${pageNumber}`;
  try {
    const response = await axios.get(url);
    return response.data;
  } catch (error) {
    return { notes: null, pages: 1 };
  }
}

export async function getNoteById(id) {
  const response = await axios.get(`${API_URL}/notes/${id}`);
  return response.data;
}

export async function createNote() {
  const response = await axios.post(`${API_URL}/notes`);
  return response.data;
}

export async function updateNote(id, note) {
  const response = await axios.put(`${API_URL}/notes/${id}`, note);
  return response.data;
}

export async function openNoteById(id) {
  const response = await axios.post(`${API_URL}/notes/${id}/open`);
  return response.data;
}

export async function deleteNote(id) {
  const response = await axios.delete(`${API_URL}/notes/${id}`);
  return response.data;
}

export async function updateNoteEmbedding(id) {
  const response = await axios.post(`${API_URL}/embed/${id}`);
  return response.data;
}

// ----- Tags API ----- //

export async function getTags() {
  try {
    const response = await axios.get(`${API_URL}/tags`);
    return response.data;
  } catch (error) {
    return { tags: [] };
  }
}

export async function getTagById(id) {
  const response = await axios.get(`${API_URL}/tags/${id}`);
  return response.data;
}

export async function createTag(tag) {
  const response = await axios.post(`${API_URL}/tags`, tag);
  return response.data;
}

export async function updateTag(id, tag) {
  const response = await axios.put(`${API_URL}/tags/${id}`, tag);
  return response.data;
}

export async function deleteTag(id) {
  const response = await axios.delete(`${API_URL}/tags/${id}`);
  return response.data;
}

export async function addTagToNote(noteId, tagId) {
  const response = await axios.post(`${API_URL}/notes/${noteId}/tags/${tagId}`);
  return response.data;
}

export async function removeTagFromNote(noteId, tagId) {
  const response = await axios.delete(
    `${API_URL}/notes/${noteId}/tags/${tagId}`
  );
  return response.data;
}

// ----- Chat API ----- //

export async function chat(messages) {
  const response = await axios.post(`${API_URL}/chat`, { messages });
  return response.data;
}

// ----- Media API ----- //

export async function uploadRecording(blob) {
  const formData = new FormData();
  formData.append("webm", blob);
  try {
    const response = await axios.post(`${API_URL}/media`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  } catch (error) {
    return false;
  }
}

export async function addMediaToNote(noteId, mediaId) {
  const response = await axios.post(
    `${API_URL}/notes/${noteId}/media/${mediaId}`
  );
  return response.data;
}

export async function getMediaById(id) {
  // request blob
  const response = await axios.get(`${API_URL}/media/${id}`, {
    responseType: "blob",
  });
  return response.data;
}

// ----- Transcription API ----- //

export async function transcribeRecording(mediaId) {
  const response = await axios.post(`${API_URL}/transcribe/${mediaId}`);
  return response.data;
}
