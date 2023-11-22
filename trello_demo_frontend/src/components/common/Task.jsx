import React, { useState } from "react";
import "./styles.scss";
import { Draggable } from "react-beautiful-dnd";
import { AiOutlineDelete } from "react-icons/ai";
import TaskModal from "./TaskModal";
import DeleteModal from "./DeleteModal";
import { deleteTask, getColumns, updateTask } from "../apis/task";
import { message } from "antd";
import { useDispatch } from "react-redux";

const Task = ({ task, index }) => {
  const [openTaskModal, setOpenTaskModal] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);
  const [openDeleteModal, setOpenDeleteModal] = useState(false);

  const dispatch = useDispatch();

  const handleCloseTaskModal = () => {
    setOpenTaskModal(false);
    setSelectedTask(null);
  };

  const handleCloseDeleteModal = () => {
    setOpenDeleteModal(false);
    setSelectedTask(null);
  };

  const handleGetTask = (value) => setSelectedTask(value);

  const handleDeleteTask = async () => {
    try {
      await deleteTask(selectedTask.task_id, selectedTask.columnId);
      message.success("Task has been deleted successfully");
      dispatch(getColumns());
      handleCloseDeleteModal();
    } catch (error) {
      let errorMessage =
        error.response?.data?.message || "Task could not be deleted";
      message.error(errorMessage);
    }
  };

  const handleUpdateTask = async (values) => {
    try {
      let body = {
        task_id: selectedTask.task_id,
        column_id: selectedTask.columnId,
        task_name: values.taskName,
        description: values.description,
        index: selectedTask.index,
      };
      await updateTask(body);
      message.success("Task has been updated successfully");
      dispatch(getColumns());
      handleCloseTaskModal();
    } catch (error) {
      let errorMessage =
        error.response?.data?.message || "Task could not be updated";
      message.error(errorMessage);
    }
  };

  return (
    <div key={index}>
      <Draggable
        draggableId={`task-${task.task_id}`}
        index={index}
        key={`task-${task.task_id}`}
      >
        {(provider) => (
          <div
            className="task-wrapper"
            {...provider.dragHandleProps}
            {...provider.draggableProps}
            ref={provider.innerRef}
          >
            <div
              className="task"
              onClick={() => {
                setOpenTaskModal(true);
                handleGetTask(task);
              }}
            >
              <div className="name">{task.task_name}</div>
              <div
                className="delete-button"
                onClick={(event) => {
                  event.stopPropagation();
                  setOpenDeleteModal(true);
                  handleGetTask(task);
                }}
              >
                <AiOutlineDelete className="icon" />
              </div>
            </div>
          </div>
        )}
      </Draggable>
      <TaskModal
        open={openTaskModal}
        onOk={handleUpdateTask}
        title={"Update Task"}
        data={selectedTask}
        onClose={handleCloseTaskModal}
        okText={"Update"}
      />
      <DeleteModal
        open={openDeleteModal}
        title={"Delete Task"}
        data={selectedTask}
        onOk={handleDeleteTask}
        onClose={handleCloseDeleteModal}
        okText={"Yes"}
      />
    </div>
  );
};

export default Task;
