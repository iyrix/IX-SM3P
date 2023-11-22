import React, { useEffect } from "react";
import "./styles.scss";
import { DragDropContext } from "react-beautiful-dnd";

import { Column } from "../common/Column";
import { getColumns, moveTasks } from "../apis/task";

import { useSelector } from "react-redux";
import { useDispatch } from "react-redux";
import { setOnDragColumns } from "../slices/columns";
import { message } from "antd";

const Landing = () => {
  const columns = useSelector((state) => state.columns.list);
  const dispatch = useDispatch();

  const onDragEnd = async (event) => {
    const { destination, source } = event;
    if (!destination) return;

    if (
      destination.droppableId === source.droppableId &&
      destination.index === source.index
    )
      return;

    let tempColumns = JSON.parse(JSON.stringify(columns));

    if (destination.droppableId === source.droppableId) {
      let columnIndex = tempColumns
        .map((item) => `column-${item.id}`)
        .indexOf(source.droppableId);
      let columnTasks = [...tempColumns[columnIndex].tasks];

      let [removed] = columnTasks.splice(source.index, 1);
      columnTasks.splice(destination.index, 0, removed);
      columnTasks = columnTasks.map((item, index) => {
        return { ...item, index: String(index + 1) };
      });

      tempColumns[columnIndex].tasks = columnTasks;
      dispatch(setOnDragColumns(tempColumns));

      let sourceColumnId = source.droppableId.split('column-')

      let tempSource = {
        columnId: String(sourceColumnId[1]),
        tasks: columnTasks,
      };
      moveTasks(tempSource).catch((err) => {
        let errorMessage =
          err.response?.data?.message || "Tasks could not be saved";
        message.error(errorMessage);
      });
    } else {
      let sourceColumnIndex = tempColumns
        .map((item) => `column-${item.id}`)
        .indexOf(source.droppableId);
      let sourceColumnTasks = [...tempColumns[sourceColumnIndex].tasks];

      let destinationColumnIndex = tempColumns
        .map((item) => `column-${item.id}`)
        .indexOf(destination.droppableId);
      let destinationColumnTasks = [
        ...tempColumns[destinationColumnIndex].tasks,
      ];

      let [removed] = sourceColumnTasks.splice(source.index, 1);

      destinationColumnTasks.splice(destination.index, 0, removed);

      sourceColumnTasks = sourceColumnTasks.map((item, index) => {
        return { ...item, index: String(index + 1) };
      });

      destinationColumnTasks = destinationColumnTasks.map((item, index) => {
        return { ...item, index: String(index + 1) };
      });

      tempColumns[sourceColumnIndex].tasks = sourceColumnTasks;
      tempColumns[destinationColumnIndex].tasks = destinationColumnTasks;

      dispatch(setOnDragColumns(tempColumns));

      let sourceColumnId = source.droppableId.split('column-')
      let destinationColumnId = destination.droppableId.split('column-')

      
      let tempSource = {
        columnId: String(sourceColumnId[1]),
        tasks: sourceColumnTasks,
        removedTask: removed,
      };
      let tempDestination = {
        columnId: String(destinationColumnId[1]),
        tasks: destinationColumnTasks,
      };

      moveTasks(tempSource, tempDestination).catch((err) => {
        let errorMessage =
          err.response?.data?.message || "Tasks could not be saved";
        message.error(errorMessage);
      });
    }
  };

  useEffect(() => {
    dispatch(getColumns());
  }, []);

  return (
    <div className="landing-container">
      <div className="heading">Task Manager</div>
      <DragDropContext onDragEnd={onDragEnd}>
        <div className="landing-wrapper">
          {columns.map((item, index) => (
            <Column item={item} index={index} />
          ))}
        </div>
      </DragDropContext>
    </div>
  );
};

export default Landing;
