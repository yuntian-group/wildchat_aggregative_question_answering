import axios, { AxiosResponse } from "axios";

const api = axios.create({
  baseURL: "http://65.108.32.135:8000",
  timeout: 10000,
  headers: {
    "Access-Control-Allow-Origin": "*",
    "Content-Type": "application/json",
  },
});

export const getTaxonomy = async () => {
  const response: AxiosResponse = await api.get("/get_label_hierarchy");
  return response.data;
};

export const getAllCountry = async () => {
  const response: AxiosResponse = await api.get("/get_all_country");
  return response.data;
};

export const getAllLanguage = async () => {
  const response: AxiosResponse = await api.get("/get_all_language");
  return response.data;
};

export const getUserList = async (query: string) => {
  if (query === "") {
    const response: AxiosResponse = await api.get(`/get_user_list`);
    return response.data;
  } else {
    const response: AxiosResponse = await api.get(
      `/get_user_list?query=${query}`
    );
    return response.data;
  }
};

export const getKeywordsList = async (query: string) => {
  if (query === "") {
    const response: AxiosResponse = await api.get(`/get_keywords_list`);
    return response.data;
  } else {
    const response: AxiosResponse = await api.get(
      `/get_keywords_list?query=${query}`
    );
    return response.data;
  }
};

export const getKeywordsAggregatedList = async (query: string) => {
  if (query === "") {
    const response: AxiosResponse = await api.get(`/get_keywords_aggregated_list`);
    return response.data;
  } else {
    const response: AxiosResponse = await api.get(
      `/get_keywords_aggregated_list?query=${query}`
    );
    return response.data;
  }
};

export const getDialgoues = async (data: Record<string, any>) => {
  const response: AxiosResponse = await api.post("/get_dialgoues", data);
  return response.data;
};

export const getDialogueContextByQuestionHash = async (hash: string) => {
  const response: AxiosResponse = await api.get(`/get_dialogue_context_by_question_hash?hash=${hash}`);
  return response.data;
}

export const getQuestionList = async (condition?: string, target?: string) => {

  let query = `/get_question_list`;

  if (condition) {
    query += `?condition=${condition}`;
  } else {
    query += `?condition=`;
  }

  if (target) {
    query += `&target=${target}`;
  }

  const response: AxiosResponse = await api.get(query);
  return response.data;
};


export const getQuestionByHash = async (hash: string) => {
  const response: AxiosResponse = await api.get(`/get_question_by_hash?hash=${hash}`);
  return response.data;
}

export const getAnnotationExamples = async () => {
  const response: AxiosResponse = await api.get(`/get_annotation_examples`);
  return response.data;
}