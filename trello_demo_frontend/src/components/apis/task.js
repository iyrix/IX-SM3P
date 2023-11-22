import axios from "axios";
import { setColumns } from "../slices/columns";
import { message } from "antd";

let baseURL = process.env.REACT_APP_BASE_URL;

export const addTask = (body) =>
  new Promise((resolve, reject) => {
    axios
      .post(`${baseURL}/task_routes/tasks`, body)
      .then((response) => {
        resolve(response.data);
      })
      .catch((err) => {
        reject(err);
      });
  });

export const updateTask = (body) =>
  new Promise((resolve, reject) => {
    axios
      .put(`${baseURL}/task_routes/tasks`, body)
      .then((response) => {
        resolve(response.data);
      })
      .catch((err) => {
        reject(err);
      });
  });

export const deleteTask = (taskId, columnId) =>
  new Promise((resolve, reject) => {
    axios
      .delete(`${baseURL}/task_routes/tasks/${taskId}/${columnId}`)
      .then((response) => {
        resolve(response.data);
      })
      .catch((err) => {
        reject(err);
      });
  });

export const getColumns = () => (dispatch) =>
  new Promise((resolve, reject) => {
    axios
      .get(`${baseURL}/columns_routes/columns`)
      .then((response) => {
        let tempArray = response.data.data
        tempArray = tempArray.length === 0 ? [] : tempArray.map((col)=>{
          let tasks = col.tasks
          tasks.sort((a , b)=>a.index - b.index)
          return {...col , tasks}
        })

        dispatch(setColumns(tempArray));
        resolve(tempArray);
      })
      .catch((err) => {
        let errorMessage =
          err.response?.data?.message || "Columns could not be loaded";
        message.error(errorMessage);
      });
  });

export const moveTasks = (source_column = null, destination_column = null) =>
  new Promise((resolve, reject) => {
    axios
      .put(`${baseURL}/task_routes/move_task`, { source_column, destination_column })
      .then((response) => {
        resolve(response.data);
      })
      .catch((err) => {
        reject(err);
      });
  });
