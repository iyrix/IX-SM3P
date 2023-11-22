import React, { useState } from "react";
import "./styles.scss";
import Task from "./Task";
import { Droppable } from "react-beautiful-dnd";
import TaskModal from "./TaskModal";
import { addTask, getColumns } from "../apis/task";
import uuid4 from "uuid4";
import { message } from "antd";
import { useDispatch } from "react-redux";

export const Column = ({ item, index }) => {
  const [openTaskModal, setOpenTaskModal] = useState(false);

  const dispatch = useDispatch()

  const handleCloseTaskModal = () => setOpenTaskModal(false);

  const handleAddTask = async (values) => {
    try {
      let tempTasks = [...item.tasks]
      tempTasks.sort((a , b)=> b?.index - a?.index)

      var id = uuid4();
      let body = {
        column_id: item.id,
        task_name: values.taskName,
        description: values.description,
        task_id: id,
        index: tempTasks.length === 0 ? String(tempTasks.length + 1) : String(tempTasks[0].index + 1)
      };
      await addTask(body);
      dispatch(getColumns())
      handleCloseTaskModal();
      message.success("Task has been created successfully")

    } catch (error) {
      let errorMessage = error.response?.data?.message || "Task could not be added"
      message.error(errorMessage)
      throw new Error(errorMessage)
    }

  };

  return (
    <div className="column-wrapper" key={index}>
      <div className="column-header">
        <div className="header">{item.name}</div>
        <div className="add-task" onClick={() => setOpenTaskModal(true)}>
          Add Task
        </div>
      </div>
      <Droppable droppableId={`column-${item?.id}`}>
        {(provider) => (
          <div
            className="drop-section"
            ref={provider.innerRef}
            {...provider.droppableProps}
          >
            {item.tasks.map((task, index) => (
              <Task task={{ ...task, columnId: item.id }} index={index} />
            ))}
            {provider?.placeholder}
          </div>
        )}
      </Droppable>

      <TaskModal
        open={openTaskModal}
        title={"Add New Task"}
        onOk={handleAddTask}
        onClose={handleCloseTaskModal}
        okText={"Add"}
      />
    </div>
  );
};
