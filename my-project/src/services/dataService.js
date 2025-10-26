import api from './api';

export const uploadFile = async (file, onUploadProgress) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress,
  });
  return response;
};

export const getDatasets = async () => {
  const response = await api.get('/data/datasets');
  return response;
};

export const getDatasetData = async (datasetId, params = {}) => {
  const response = await api.get(`/data/${datasetId}`, { params });
  return response;
};

export const getDatasetMetadata = async (datasetId) => {
  const response = await api.get(`/data/${datasetId}/metadata`);
  return response;
};

export const getChartData = async (datasetId, column, aggregation = 'count') => {
  const response = await api.get(`/data/${datasetId}/summary`, {
    params: { column, aggregation },
  });
  return response;
};

export const deleteDataset = async (datasetId) => {
  const response = await api.delete(`/data/${datasetId}`);
  return response;
};
