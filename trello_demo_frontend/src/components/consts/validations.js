import * as Yup from 'yup'

export const taskModalValidation = Yup.object().shape({
    taskName: Yup.string().required("Task name is required*").trim(),
  });

