import axios from "axios";

import { API_URL } from "./constants";

// Wrapper for axios to make API calls

async function apiCall(method, endpoint, data = null) {
  const url = `${API_URL}${endpoint}`;
  try {
    switch (method) {
      case "get":
        return await axios.get(url);
      case "post":
        return await axios.post(url, data);
      case "put":
        return await axios.put(url, data);
      case "delete":
        return await axios.delete(url);
      default:
        return null;
    }
  } catch (error) {
    console.error(error);
    return null;
  }
}

// ----- Health API ----- //

export async function getHealth() {
  const response = await apiCall("get", "/health");
  return response.data;
}

// ----- Notes API ----- //

export async function getNotes(
  query = null,
  sortBy = "opened",
  tags = [],
  resultsPerPage = 10,
  pageNumber = 1
) {
  let url = `/notes?`;
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

  const response = await apiCall("get", url);
  return response.data;
}

export async function getNoteById(id) {
  const response = await apiCall("get", `/notes/${id}`);
  return response.data;
}

export async function createNote() {
  const response = await apiCall("post", "/notes");
  return response.data;
}

export async function updateNote(id, note) {
  const response = await apiCall("put", `/notes/${id}`, note);
  return response.data;
}

export async function openNoteById(id) {
  const response = await apiCall("post", `/notes/${id}/open`);
  return response.data;
}

export async function deleteNote(id) {
  const response = await apiCall("delete", `/notes/${id}`);
  return response.data;
}

export async function updateNoteEmbedding(id) {
  const response = await apiCall("post", `/embed/${id}`);
  return response.data;
}

// ----- Tags API ----- //

export async function getTags() {
  const response = await apiCall("get", "/tags");
  return response.data;
}

export async function getTagById(id) {
  const response = await apiCall("get", `/tags/${id}`);
  return response.data;
}

export async function createTag(tag) {
  const response = await apiCall("post", "/tags", tag);
  return response.data;
}

export async function updateTag(id, tag) {
  const response = await apiCall("put", `/tags/${id}`, tag);
  return response.data;
}

export async function deleteTag(id) {
  const response = await apiCall("delete", `/tags/${id}`);
  return response.data;
}

export async function addTagToNote(noteId, tagId) {
  const response = await apiCall("post", `/notes/${noteId}/tags/${tagId}`);
  return response.data;
}

export async function removeTagFromNote(noteId, tagId) {
  const response = await apiCall("delete", `/notes/${noteId}/tags/${tagId}`);
  return response.data;
}

// ----- Chat, Summary, and RAG API ----- //

export async function chat(messages) {
  const response = await apiCall("post", "/chat", { messages });
  return response.data;
}

export async function summarize(text) {
  const response = await apiCall("post", "/summarize", { text });
  return response.data;
}

export async function getNotesByQuery(query, nResults) {
  const response = await apiCall("post", "/rag", { query, nResults });
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

export async function getMediaById(id) {
  // request blob
  const response = await axios.get(`${API_URL}/media/${id}`, {
    responseType: "blob",
  });
  return response.data;
}

export async function addMediaToNote(noteId, mediaId) {
  const response = await apiCall("post", `/notes/${noteId}/media/${mediaId}`);
  return response.data;
}

// ----- Transcription API ----- //

export async function transcribeRecording(mediaId) {
  const response = await apiCall("post", `${API_URL}/transcribe/${mediaId}`);
  return response.data;
}
