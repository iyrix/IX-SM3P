import { configureStore } from "@reduxjs/toolkit";
import columnReducer from "./components/slices/columns";


export const store = configureStore({
    reducer : {
        columns : columnReducer,

    },
})