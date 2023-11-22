import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  list: [
    {
      id: "1",
      name: "To Do",
      tasks: [],
    },
    {
      id: "2",
      name: "In Progress",
      tasks: [],
    },
    {
      id: "3",
      name: "Done",
      tasks: [],
    },
  ],
};

export const columnSlice = createSlice({
  name: "columns",
  initialState,
  reducers: {
    setColumns: (state, actions) => {
        console.log("Action: " , actions.payload);
        let tempArray = [...actions.payload]

        tempArray = state.list.length === 0 ? [] : state.list.map((item) => {
            let column = tempArray.find((resCol) => item?.id === resCol?.column_id);
            if (column) {
              return { ...item, tasks: column.tasks };
            }
            return item;
          });

      state.list = [...tempArray];
    },
    setOnDragColumns: (state , actions) =>{
        state.list = actions.payload

    }
  },
});

export const { setColumns , setOnDragColumns } = columnSlice.actions;

export default columnSlice.reducer;
