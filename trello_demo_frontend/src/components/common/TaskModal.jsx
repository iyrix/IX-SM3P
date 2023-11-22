import React, { useState } from "react";
import { Form, Input, Modal } from "antd";
import { Formik } from "formik";
import { taskModalValidation } from "../consts/validations";
const { TextArea } = Input;

const TaskModal = ({ open, onClose, onOk, title, okText, data }) => {
  const [loading, setLoading] = useState(false);

  const onSubmit = async (values , actions) => {
    try {
      setLoading(true);
      await onOk(values);
      actions.setValues({
        taskName : "",
        description : ""
      })
      setLoading(false);
    } catch (error) {
      setLoading(false);
    }
  };
  return (
    <Formik
      initialValues={{
        taskName: data ? data.task_name : "",
        description: data ? data.description : "",
      }}
      validationSchema={taskModalValidation}
      validateOnChange={true}
      enableReinitialize={true}
      onSubmit={onSubmit}
    
    >
      {({ errors, handleSubmit, setValues, values }) => (
        <Form>
          <Modal
            title={title}
            open={open}
            onOk={handleSubmit}
            onCancel={onClose}
            okText={okText}
            confirmLoading={loading}
            okButtonProps={{
              disabled : Object.entries(errors).length
            }}
          >
            <div className="task-modal-wrapper">
              <div className="input-wrapper">
                <div className="label">
                  Task Name <b>*</b>
                </div>
                <Input
                  placeholder="Please enter task name"
                  name="taskName"
                  value={values.taskName}
                  onChange={(event) =>
                    setValues({ ...values, taskName: event.target.value })
                  }
                />
                {errors?.taskName && (
                  <div className="error-message">{errors.taskName}</div>
                )}
              </div>
              <div className="text-area-wrapper">
                <div className="label">Description</div>
                <TextArea
                  name="description"
                  value={values.description}
                  rows={4}
                  placeholder="Please enter description"
                  onChange={(event) =>
                    setValues({ ...values, description: event.target.value })
                  }
                />
                {errors?.description && (
                  <div className="error-message">{errors.description}</div>
                )}
              </div>
            </div>
          </Modal>
        </Form>
      )}
    </Formik>
  );
};

export default TaskModal;
